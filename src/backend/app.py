import logging
import asyncio
import json
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
from src.backend.config import config
from src.backend.internal.lru_cache import CustomLRUCache
from src.backend.internal.thread_safe_set import ThreadSafeSet
from src.backend.routes import router


CRED_DICT = json.loads(config.GOOGLE_APPLICATION_CREDENTIALS)
CRED = credentials.Certificate(CRED_DICT)
firebase_admin.initialize_app(CRED)
DB_COLLECTION_NAME = config.DB_COLLECTION_NAME

# Initialize Firestore client
db: Client = firestore.client()
cache = CustomLRUCache(config.LRU_CACHE_SIZE, db)
if config.ENVIRONMENT == "DEV":
    logging.basicConfig(level=logging.DEBUG, force=True)
elif config.ENVIRONMENT == "PROD":
    logging.basicConfig(level=logging.INFO, force=True)

# lifespan function to manage background tasks
async def prune_db(db: Client, interval_hours: int):
    """
    Periodically scans Firestore and deletes documents older than 'expireAt'.

    Args:
        db: Firestore client
        interval_days (int): How often to run the scan (in hours)
    """
    while True:  # run immediatelly on app startup to remove unused items in db
        try:
            now = datetime.now(timezone.utc)
            logging.info(f"[{now}] Running Firestore cleanup")

            # Use FieldFilter to avoid the positional argument warning
            from google.cloud.firestore import FieldFilter

            docs = (
                db.collection(DB_COLLECTION_NAME)
                .where(filter=FieldFilter("expireAt", "<", now))
                .stream()
            )

            deleted_count = 0
            # Use regular for loop, not async for - Firestore stream() is synchronous
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1

            logging.info(f"Deleted {deleted_count} expired documents.")

        except Exception as e:
            logging.error("Error during Firestore cleanup: %s", e)

        # Wait interval before next scan
        await asyncio.sleep(interval_hours * 3600)


def load_existing_ids(db: Client) -> ThreadSafeSet:
    projects_ref = db.collection(DB_COLLECTION_NAME)
    docs = projects_ref.stream()

    all_ids = ThreadSafeSet()
    for doc in docs:
        file_name = doc.id
        session_id = file_name.partition(":")[2]
        all_ids.add(session_id)
    return all_ids


async def scan_cache(cache: CustomLRUCache, interval: int, run_once: bool = False):
    """
    Scans through cache and syncs required data to firestore

    Args:
        cache: CustomLRUCache class instance
        inverval (int): How often to scan through cache(minutes)
    """
    synced_sessions = 0
    while True:
        if not run_once:
            await asyncio.sleep(interval * 60)  # no need to run on app startup
        logging.info("Starting Cache Scan")
        start_time = time.time()
        for session_id, grid_manager in cache.items():
            if not grid_manager.requires_sync:
                continue
            try:
                cache.sync_to_firebase(session_id, grid_manager)
                logging.info("Synced session: %s", session_id)
                synced_sessions += 1
            except Exception as e:
                logging.error("Error during cache scan: %s", e)
        logging.info(
            "Cache scan complete, synced %s sessions. Duration: %ss.",
            synced_sessions,
            time.time() - start_time,
        )
        if run_once:
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    task1 = asyncio.create_task(prune_db(db, config.PRUNE_DB_INTERVAL))
    loaded_ids = load_existing_ids(db)
    app.state.all_ids = loaded_ids
    task2 = asyncio.create_task(scan_cache(cache, config.SCAN_CACHE_INTERVAL))
    logging.info("Background tasks started")

    yield

    # begin shutdown
    logging.info("Shut down background tasks")
    task1.cancel()
    task2.cancel()
    try:
        await asyncio.gather(task1, task2)
    except asyncio.CancelledError:
        pass  # expected during shutdown
    # run cache scan one more time to sync all data to firestore
    if config.ENVIRONMENT != "DEV":  # don't save in dev to avoid overloading database
        logging.info("Syncing changes before shutdown")
        await scan_cache(cache, config.SCAN_CACHE_INTERVAL, run_once=True)
    logging.info("Shutdown Complete")

def create_app(use_lifespan:bool=True):
    app = FastAPI(lifespan=lifespan if use_lifespan else None)
    app.include_router(router)
    app.state.manager_cache = cache
    app.state.db = db
    return app

app = create_app()

# CORS configuration
origins = ["http://localhost:8080",
           config.FRONT_END_DOMAIN
           ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for API Key authentication for protected endpoints
INCLUDED_PATHS = ["/cached_items","/cached_items/","/session_exists","/session_exists/"]
API_KEY_NAME = "x-api-key"

class APIKEYMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        #skip excluded paths
        if not any(request.url.path.startswith(path) for path in INCLUDED_PATHS):
            return await call_next(request)
        
        api_key = request.headers.get(API_KEY_NAME)
        if api_key != config.API_KEY:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Invalid or missing API Key"})
        return await call_next(request)

app.add_middleware(APIKEYMiddleware)
