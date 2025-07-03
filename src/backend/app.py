import io
import base64
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import cast
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from cachetools import LRUCache
from typing import Literal
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
from src.backend.config import config
from src.backend.internal.grid_manager import GridManager, GridHandler
import src.backend.internal.time_blocks as tb
from src.backend.internal.lru_cache import CustomLRUCache

cred_path = config.GOOGLE_APPLICATION_CREDENTIALS
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db: Client = firestore.client()
cache = CustomLRUCache(config.LRU_CACHE_SIZE, db)
logging.basicConfig(level=logging.DEBUG, force=True)


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
                db.collection("projects")
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


def load_existing_ids(db: Client):
    projects_ref = db.collection("projects")
    docs = projects_ref.stream()

    all_ids = set()
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
    if config.ENVIRONMENT != "DEV": #don't save in dev to avoid overloading database
        logging.info("Syncing changes before shutdown")
        await scan_cache(cache, config.SCAN_CACHE_INTERVAL, run_once=True)
    logging.info("Shutdown Complete")


app = FastAPI(lifespan=lifespan)
app.state.manager_cache = cache
app.state.db = db


def restore_from_database(session_id: str) -> GridManager:
    """
    Restore GridManager Instance using saved data in firestore

    Args:
        session_id(str): session_id to

    Returns:
        GridManager class instance
    """
    doc_ref = db.collection("projects").document(f"session_id:{session_id}")
    doc = doc_ref.get()
    data = doc.to_dict()
    decoded_bytes = base64.b64decode(data.get("data"))
    manager = GridManager.deserialise_from_zip(decoded_bytes)
    return manager


def get_manager(x_session_id: str = Header(...)) -> GridManager:
    logging.debug(x_session_id)
    cache = app.state.manager_cache
    cache = cast(LRUCache, cache)
    if x_session_id in cache:
        logging.debug("Cache hit, returning cached manager")
        manager = cache[x_session_id]
        manager.requires_sync = True
        return manager
    if x_session_id in app.state.all_ids:  # check if can load from firebase
        manager = restore_from_database(x_session_id)
        logging.debug("Restored from database")
    else:  # create new manager
        manager = GridManager()
        logging.debug("Cache miss,Creating new manager")
        app.state.all_ids.add(x_session_id)
    cache[x_session_id] = manager
    manager.requires_sync = True
    return manager


# Request body schema
class UploadRequest(BaseModel):
    session_id: str
    project_name: str
    data: dict


class FetchGridRequest(BaseModel):
    day: Literal[1, 2, 3]


class AddOrRemoveRequest(BaseModel):
    grid_name: Literal[
        "DAY1:MCC",
        "DAY1:HCC1",
        "DAY1:HCC2",
        "DAY2:MCC",
        "DAY2:HCC1",
        "DAY2:HCC2",
        "DAY3:MCC",
    ]
    name: str


class AllocateShiftRequest(AddOrRemoveRequest):
    location: Literal["MCC", "HCC1", "HCC2"]
    allocation_size: Literal["0.25", "0.75", "1"]
    time_block: str


@app.get("/all_ids/")
def all_ids():
    """
    Load all existing session ids on startup

    Args:
        db: Firestore client
    """

    return {"data": list(app.state.all_ids)}


@app.get("/cached_items/")
async def get_num_cached_items():
    cache: CustomLRUCache = app.state.manager_cache
    response = {"current_size": cache.currsize, "num_items": len(cache.items())}
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@app.get("/session_exists/")
async def session_exists(session_id: str):
    response = {"exists": session_id in app.state.all_ids}
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@app.post("/grid/")  # get all grid data for a specified day
async def get_grid(
    request: FetchGridRequest, manager: GridManager = Depends(get_manager)
):
    result = {}
    bit_masks = {}
    day = request.day
    # find the required handlers
    for key, handler in manager.all_grids.items():
        if f"DAY{day}" not in key:
            continue
        num = len(bit_masks) + 1
        bit_masks[f"bit_mask_{num}"] = handler.bit_mask

    # format the keys
    blocks_to_remove = manager.format_keys(tb.HALF_DAY_BLOCK_MAP[day], **bit_masks)

    # get the formatted dataframe in aggrid format
    for key, handler in manager.all_grids.items():
        if f"DAY{day}" not in key:
            continue
        handler = cast(GridHandler, handler)
        formatted_df = handler.generate_formatted_dataframe(blocks_to_remove)
        aggrid_format = handler.df_to_aggrid_format(formatted_df)
        result[key] = aggrid_format
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.post("/grid/compressed")
async def get_grid_compressed(
    request: FetchGridRequest, manager: GridManager = Depends(get_manager)
):
    day = request.day
    if day != 3:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Call for day 3 grid only"},
        )
    handler = manager.all_grids["DAY3:MCC"]
    handler = cast(GridHandler, handler)
    blocks_to_remove = manager.format_keys(tb.HALF_DAY_BLOCK_MAP[day], handler.bit_mask)
    formatted_df = handler.generate_formatted_dataframe(blocks_to_remove)
    aggrid_format_compressed = handler.df_to_aggrid_compressed(formatted_df)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=aggrid_format_compressed
    )


@app.post("/grid/add/")
async def add_name(
    request: AddOrRemoveRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = request.grid_name
    day = target_grid[3]
    name = request.name.upper()
    if manager.name_exists(name, day):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": f"{name} already exists in DAY:{day}"},
        )

    grid_handler = manager.all_grids[target_grid]
    grid_handler = cast(GridHandler, grid_handler)
    if name.upper() in grid_handler.get_names():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": f"{name} already exists in {target_grid}"},
        )
    grid_handler.add_name(name)
    manager.update_existing_names(day)
    manager.update_hours(name, target_grid)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"detail": f"{name} added to {target_grid}"},
    )


@app.delete("/grid/remove/")
async def remove_name(
    request: AddOrRemoveRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = request.grid_name
    day = target_grid[3]
    name = request.name.upper()
    grid_handler = manager.all_grids[target_grid]
    grid_handler = cast(GridHandler, grid_handler)
    if name.upper() not in grid_handler.get_names():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{name} does not exist in {target_grid}"},
        )
    grid_handler.remove_name(name)
    manager.update_existing_names(day)
    manager.update_hours(name, target_grid)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": f"Removed {name} from {target_grid}"},
    )


@app.post("/grid/allocate/")
async def allocate_shift(
    request: AllocateShiftRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = request.grid_name
    name = request.name.upper()
    grid_handler = manager.all_grids[target_grid]
    grid_handler = cast(GridHandler, grid_handler)
    if name.upper() not in grid_handler.get_names():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{name} does not exist in {target_grid}"},
        )

    # time_block --> "08:00", "08:30" etc
    # allocation_size --> 0.25 (first half), 0.75 (second half), 1 (full hour)
    location = request.location
    time_block = request.time_block
    allocation_size = request.allocation_size
    if ":30" in time_block and allocation_size != "0.75":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "For time_blocks ending with :30, should have allocation size 0.75 only"
            },
        )
    if allocation_size == "1":
        grid_handler.allocate_shift(location, time_block, name)
        second_half = time_block[:-2] + "30"
        grid_handler.allocate_shift(location, second_half, name)

    elif allocation_size == "0.25":
        grid_handler.allocate_shift(location, time_block, name)
    elif allocation_size == "0.75":
        second_half = time_block[:-2] + "30"
        grid_handler.allocate_shift(location, second_half, name)
    manager.update_hours(name, target_grid)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": f"Allocated: {target_grid},{name},{time_block},{allocation_size},{location}"
        },
    )


@app.get("/hours/")
async def get_all_hours(request: Request, manager: GridManager = Depends(get_manager)):
    row_data, pinned_row_data = manager.get_all_hours()
    response = {
        "columnDefs": [
            {
                "headerName": "Name",
                "field": "Name",
                "width": 100,
                "suppressSizeToFit": True,
            },
            {
                "headerName": "Day 1",
                "field": "Day 1",
                "flex": 1,
                "resizable": False,
            },
            {
                "headerName": "Day 2",
                "field": "Day 2",
                "flex": 1,
                "resizable": False,
            },
            {
                "headerName": "Day 3",
                "field": "Day 3",
                "flex": 1,
                "resizable": False,
            },
            {
                "headerName": "Total",
                "field": "Total",
                "flex": 1,
                "resizable": False,
            },
        ],
        "rowData": row_data,
        "pinned_bottom_row": pinned_row_data,
    }
    return response


@app.post("/download/")
async def save_as_file(request: Request, manager: GridManager = Depends(get_manager)):
    try:
        zip_bytes = manager.serialise_to_zip()
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=planning.zip"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed:{str(e)}")


@app.post("/upload/")
async def upload_file(request: Request, manager: GridManager = Depends(get_manager)):
    try:
        zip_bytes = await request.body()
        manager_instance = GridManager.deserialise_from_zip(zip_bytes)
        app.state.manager_cache[request.headers["X-Session-ID"]] = manager_instance
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "ok"})
    except Exception as e:
        logging.debug(f"{str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error: likely invalid/corrupted zip file"
            },
        )


@app.delete("/reset-all/")
async def reset_all(request: Request, manager: GridManager = Depends(get_manager)):
    app.state.manager_cache[request.headers["X-Session-ID"]] = GridManager()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"detail": "data resetted"}
    )
