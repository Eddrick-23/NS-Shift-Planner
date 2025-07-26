import io
import uuid
import base64
import logging
from typing import cast
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, Depends, status, HTTPException, Request, Header, Cookie
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from google.cloud.firestore import Client
from src.backend.internal.grid_manager import GridManager, GridHandler
import src.backend.internal.time_blocks as tb
from src.backend.internal.lru_cache import CustomLRUCache
from src.backend.config import config
router = APIRouter()

DB_COLLECTION_NAME = config.DB_COLLECTION_NAME

def restore_from_database(db:Client,session_id: str) -> GridManager:
    """
    Restore GridManager Instance using saved data in firestore

    Args:
        db (Client): Firestore client instance
        session_id(str): session_id to

    Returns:
        GridManager class instance
    """
    doc_ref = db.collection(DB_COLLECTION_NAME).document(f"session_id:{session_id}")
    doc = doc_ref.get()
    data = doc.to_dict()
    decoded_bytes = base64.b64decode(data.get("data"))
    manager = GridManager.deserialise_from_zip(decoded_bytes)
    return manager

def valid_id(session_id:str, cache:CustomLRUCache, all_ids:set) -> tuple[bool,str|None]:
    """
    Checks if a session_id exists in cache or database

    Returns:
        bool: True if session_id exists
        str: where the session_id exists OR None for invalid id
    """
    if session_id in cache:
        return True, "cache"
    if session_id in all_ids:
        return True, "db"
    
    return False,None
    

def get_manager(request:Request,session_id = Cookie(..., alias="session_id")) -> GridManager:
    logging.debug(session_id)
    cache:CustomLRUCache = request.app.state.manager_cache
    all_ids:set = request.app.state.all_ids

    valid, location = valid_id(session_id,cache,all_ids)

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if location == "cache":
        logging.debug("Cache hit, returning cached manager")
        manager = cache[session_id]
    if location == "db":
        manager = restore_from_database(request.app.state.db, session_id)
        logging.debug("Restored from database")
        cache[session_id] = manager #store in cache
    manager.requires_sync = True
    return manager


# Request body schema
class UploadRequest(BaseModel):
    session_id: str
    project_name: str
    data: dict


class FetchGridRequest(BaseModel):
    day: Literal[1, 2, 3]
    location:Literal["MCC","HCC1","HCC2"]


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


class SwapNameRequest(BaseModel):
    grid_name: Literal[
        "DAY1:MCC",
        "DAY1:HCC1",
        "DAY1:HCC2",
        "DAY2:MCC",
        "DAY2:HCC1",
        "DAY2:HCC2",
        "DAY3:MCC",
    ]
    names: Annotated[list[str], Field(min_length=2, max_length=2)]

class loginRequest(BaseModel):
    session_id : str | None = None


@router.get("/login/")
async def login(request:Request, session_id: str|None = Cookie(None,alias="session_id")):
    #handle login requests
    #if there is no session id, issue an id
    #if there is a session id, authenticate it first before issuing

    #issue session id in http header
    id_valid = False
    if session_id is not None:
        valid, _ = valid_id(session_id,request.app.state.manager_cache, request.app.state.all_ids)
        id_valid = valid

    if not id_valid: #no session id or no id_valid
        session_id = str(uuid.uuid4())
        manager = GridManager()
        request.app.state.all_ids.add(session_id) #add to existing ids
        request.app.state.manager_cache[session_id] = manager #add to lru cache
    
    response = JSONResponse(status_code=status.HTTP_200_OK, content={"detail":"login successful"})

    #set session_id and in the http cookies
    if config.ENVIRONMENT == "PROD":
        response.set_cookie(key="session_id",
                            value=session_id,
                            httponly=True,
                            secure=True,
                            samesite="lax",
                            domain=config.FRONT_END_DOMAIN
                            )
    else:
        response.set_cookie(key="session_id",
                            value=session_id,
                            httponly=True,
                            secure=False,
                            samesite="lax",
                            )
    return response

@router.get("/health/")
async def health_check():
    return {"status":"ok"}


@router.get("/cached_items/") #protected
async def get_num_cached_items(request:Request):
    cache: CustomLRUCache = request.app.state.manager_cache
    response = {"current_size": cache.currsize, "num_items": len(cache.items())}
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@router.get("/session_exists/") #protected
async def session_exists(request:Request,session_id: str):
    logging.debug(request.app.state.all_ids._set)
    response = {"exists": session_id in request.app.state.all_ids}
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@router.post("/grid/")  # get all grid data for a specified day
async def get_grid(
    request:Request, fetch_grid_req:FetchGridRequest, manager: GridManager = Depends(get_manager)
):
    result = {}
    bit_masks = {}
    day = fetch_grid_req.day
    location = fetch_grid_req.location
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
        if f"DAY{day}" not in key or location not in key:
            continue
        handler = cast(GridHandler, handler)
        formatted_df = handler.generate_formatted_dataframe(blocks_to_remove)
        aggrid_format = handler.df_to_aggrid_format(formatted_df)
        result["data"] = aggrid_format
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.post("/grid/compressed")
async def get_grid_compressed(
    request: Request, fetch_grid_req:FetchGridRequest, manager: GridManager = Depends(get_manager)
):
    day = fetch_grid_req.day
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


@router.get("/grid/names/")
async def get_names(
    request: Request,
    day: int,
    grid: str,
    manager: GridManager = Depends(get_manager),
):
    target_grid = f"DAY{day}:{grid}"
    grid_handler: GridHandler = manager.all_grids.get(target_grid, None)
    if grid_handler is None:
        logging.error("Target Grid is None, may not be initialised in manager")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={}
        )
    existing_names = grid_handler.get_names()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"names": list(existing_names)}
    )


@router.post("/grid/add/")
async def add_name(
    request: Request, add_req:AddOrRemoveRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = add_req.grid_name
    day = target_grid[3]
    name = add_req.name.upper()
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


@router.delete("/grid/remove/")
async def remove_name(
    request: Request, remove_req:AddOrRemoveRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = remove_req.grid_name
    day = target_grid[3]
    name = remove_req.name.upper()
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


@router.post("/grid/allocate/")
async def allocate_shift(
    request:Request, allocate_shift_req:AllocateShiftRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = allocate_shift_req.grid_name
    name = allocate_shift_req.name.upper()
    grid_handler = manager.all_grids[target_grid]
    grid_handler = cast(GridHandler, grid_handler)
    if name not in grid_handler.get_names():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{name} does not exist in {target_grid}"},
        )

    # time_block --> "08:00", "08:30" etc
    # allocation_size --> 0.25 (first half), 0.75 (second half), 1 (full hour)
    location = allocate_shift_req.location
    time_block = allocate_shift_req.time_block
    allocation_size = allocate_shift_req.allocation_size
    #force allocation_size "0.75" for :30 time blocks
    if ":30" in time_block:
        allocation_size = "0.75"

    #for time blocks ending in :00, and allocation_size "1"
        #both half allocated/ empty -> fully allocate/deallocate
        #exactly one half allocated -> 0.25
        #both allocated but different value -> 0.25
    
    #for time blocks ending in :00 and allocation_size "0.75"
        #if second half allocated -> 0.25
    if time_block[-2:] == "00":
        first_half_allocated = grid_handler.is_shift_allocated(time_block,name)
        second_half_allocated = grid_handler.is_shift_allocated(time_block[:-2]+"30",name)
        match allocation_size:
            case "1":
                exactly_one_half_allocated = (first_half_allocated and not second_half_allocated) or (not first_half_allocated and second_half_allocated)
                both_allocated = first_half_allocated and second_half_allocated
                if exactly_one_half_allocated:
                    allocation_size = "0.25"
                elif both_allocated:
                    first_location = grid_handler.get_shift_location(time_block,name)
                    second_location = grid_handler.get_shift_location(time_block[:-2]+"30",name)
                    if first_location != second_location:
                        allocation_size = "0.25"
            case "0.75":
                if second_half_allocated:
                    allocation_size = "0.25"
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


@router.get("/hours/")
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


@router.post("/download/")
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


@router.post("/upload/")
async def upload_file(request: Request, manager: GridManager = Depends(get_manager)):
    try:
        zip_bytes = await request.body()
        manager_instance = GridManager.deserialise_from_zip(zip_bytes)
        request.app.state.manager_cache[request.headers["X-Session-ID"]] = manager_instance
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "ok"})
    except Exception as e:
        logging.debug(f"{str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error: likely invalid/corrupted zip file"
            },
        )


@router.delete("/reset-all/")
async def reset_all(request: Request, manager: GridManager = Depends(get_manager)):
    request.app.state.manager_cache[request.headers["X-Session-ID"]] = GridManager()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"detail": "data resetted"}
    )


@router.post("/grid/swap-names/")
async def swap_names(
    request:Request, swap_name:SwapNameRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = swap_name.grid_name
    names = swap_name.names
    # update handler
    grid_handler: GridHandler = manager.all_grids[target_grid]
    swapped = grid_handler.swap_names(names[0], names[1])

    # swap in GridManager hour tracking
    if not swapped:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    manager.swap_hours(names[0], names[1], target_grid)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": f"Swapped {names}, target_grid:{target_grid}"},
    )
