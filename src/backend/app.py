import logging
import asyncio
import json
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
from google.cloud.firestore import FieldFilter
from src.backend.config import config
from src.backend.internal.lru_cache import CustomLRUCache
from src.backend.routers import health, planner

from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


# setup functions
def setup_logging():
    if config.ENVIRONMENT == "DEV":
        logging.basicConfig(level=logging.DEBUG, force=True)
    elif config.ENVIRONMENT == "PROD":
        logging.basicConfig(level=logging.INFO, force=True)


def init_firebase() -> Client:
    """Initialise firebase and returns the DB Client"""
    if not firebase_admin._apps:
        CRED_DICT = json.loads(config.GOOGLE_APPLICATION_CREDENTIALS)
        CRED = credentials.Certificate(CRED_DICT)
        firebase_admin.initialize_app(CRED)

    return firestore.client()


# Background tasks
def database_remove_expired(
    db: Client, db_collection_name: str, timestamp: datetime
) -> list[str]:
    """
    Check database for documents older than timestamp. Remove those from database.

    Args:
        db: FireStore Client
        db: database collection name
        timestamp: python datetime timestamp
    Returns:
        list of removed document ids
    """
    removed = []
    try:
        docs = (
            db.collection(db_collection_name)
            .where(filter=FieldFilter("expireAt", "<", timestamp))
            .stream()
        )
        for doc in docs:
            doc.reference.delete()
            session_id = doc.id.partition(":")[2]
            removed.append(session_id)

    except Exception as e:
        logging.error("Error in firestore cleanup: %s", e)
    logging.info(f"Deleted {len(removed)} expired documents.")
    return removed


def cache_remove_expired(manager_cache: CustomLRUCache, removed_ids: list[str]):
    """
    remove expired ids from cache once pruned from database

    Args:
        manager_cache: CustomLRUCache Instance
    """
    for id in removed_ids:
        manager_cache.pop(id, None)


# TODO fix bug, prune should also remove from manager_cache and id_cache
async def prune_expired_sessions(
    db: Client,
    db_collection_name: str,
    manager_cache: CustomLRUCache,
    interval_hours: int,
):
    """
    Periodically scans Firestore and deletes documents older than 'expireAt'.
    Pruned documents are also removed from cache
    Args:
        db: Firestore client
        interval_days (int): How often to run the scan (in hours)
    """
    while True:  # run immediatelly on app startup to remove unused items in db
        try:
            now = datetime.now(timezone.utc)
            logging.info(f"[{now}] Running Firestore cleanup")

            removed = database_remove_expired(db, db_collection_name, now)
            cache_remove_expired(manager_cache, removed)

        except Exception as e:
            logging.error("Error during Firestore cleanup: %s", e)

        # Wait interval before next scan
        await asyncio.sleep(interval_hours * 3600)


async def scan_cache(cache: CustomLRUCache, interval: int, run_once: bool = False):
    """
    Scans through cache and syncs required data to firestore

    Args:
        cache: CustomLRUCache class instance
        inverval (int): How often to scan through cache(minutes)
        run_once (bool): run scan once not periodically (for dev)
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
        synced_sessions = 0  # reset counter after scan
        if run_once:
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    # create DB and cache
    db_collection_name = config.DB_COLLECTION_NAME
    db_client = init_firebase()
    manager_cache = CustomLRUCache(config.LRU_CACHE_SIZE, db_client)

    task1 = asyncio.create_task(
        prune_expired_sessions(
            db_client,
            db_collection_name,
            manager_cache,
            config.PRUNE_DB_INTERVAL,
        )
    )
    task2 = asyncio.create_task(scan_cache(manager_cache, config.SCAN_CACHE_INTERVAL))

    # store in app state
    app.state.manager_cache = manager_cache  # stored grid manager instances
    app.state.db = db_client  # firebase database client
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
        await scan_cache(manager_cache, config.SCAN_CACHE_INTERVAL, run_once=True)
    logging.info("Shutdown Complete")


def create_app(use_lifespan: bool = True):
    app = FastAPI(lifespan=lifespan if use_lifespan else None)
    app.include_router(health.router)
    app.include_router(planner.router)
    return app


app = create_app()

# CORS configuration
origins = ["http://localhost:8080", config.FRONT_END_DOMAIN]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for API Key authentication for protected endpoints
INCLUDED_PATHS = [
    "/cached_items",
    "/cached_items/",
    "/session_exists",
    "/session_exists/",
]
API_KEY_NAME = "x-api-key"


class APIKEYMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # skip excluded paths
        if not any(request.url.path.startswith(path) for path in INCLUDED_PATHS):
            return await call_next(request)

        api_key = request.headers.get(API_KEY_NAME)
        if api_key != config.API_KEY:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid or missing API Key"},
            )
        return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logging.info("Validation error on: %s", request.url)
    logging.info("Request body: %s", body.decode())
    logging.info("Validation errors: %s", exc.errors())
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


app.add_middleware(APIKEYMiddleware)
