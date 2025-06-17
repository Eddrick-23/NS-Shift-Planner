import io
from typing import cast
from fastapi import FastAPI, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse,StreamingResponse
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from src.backend.internal.grid_manager import GridManager, GridHandler
import src.backend.internal.time_blocks as tb

# Load .env to get credentials path
load_dotenv()
# cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# cred = credentials.Certificate(cred_path)
# firebase_admin.initialize_app(cred)

# # Initialize Firestore client
# db = firestore.client()

grid_manager = GridManager()
app = FastAPI()
app.state.grid_manager = grid_manager


def get_manager():
    return app.state.grid_manager


# Request body schema
class UploadRequest(BaseModel):
    user_id: str
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


# @app.post("/upload/")
# async def upload_data(request: UploadRequest):
#     doc_id = f"{request.user_id}_{request.project_name}" #document name
#     doc_ref = db.collection("projects").document(doc_id) #folder("collection") name

#     # Upload or overwrite the data using .set()
#     doc_ref.set({
#         "user_id": request.user_id,
#         "project_name": request.project_name,
#         "data": request.data
#     })

#     return {"message": "Data uploaded successfully"}


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
async def get_grid_compressed(request:FetchGridRequest, manager:GridManager=Depends(get_manager)):
    day = request.day
    if day != 3:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Call for day 3 grid only"})
    handler = manager.all_grids["DAY3:MCC"]
    handler = cast(GridHandler, handler)
    blocks_to_remove = manager.format_keys(tb.HALF_DAY_BLOCK_MAP[day], handler.bit_mask)
    formatted_df = handler.generate_formatted_dataframe(blocks_to_remove)
    aggrid_format_compressed = handler.df_to_aggrid_compressed(formatted_df)

    return JSONResponse(status_code=status.HTTP_200_OK, content=aggrid_format_compressed)



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
    grid_manager.update_existing_names(day)
    grid_manager.update_hours(name, target_grid)
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
        print(f"allocate_shift:{location, time_block, name}")
        grid_handler.allocate_shift(location, time_block, name)
    elif allocation_size == "0.75":
        second_half = time_block[:-2] + "30"
        print(f"allocate_shift:{location, second_half, name}")
        grid_handler.allocate_shift(location, second_half, name)
    manager.update_hours(name, target_grid)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": f"Allocated: {target_grid},{name},{time_block},{allocation_size},{location}"
        },
    )


@app.get("/hours/")
async def get_all_hours(manager: GridManager = Depends(get_manager)):
    row_data, pinned_row_data = manager.get_all_hours()
    response = {
        "columnDefs": [
            {
                "headerName": "Name",
                "field": "Name",
                "width": 150,
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
        "pinned_bottom_row": pinned_row_data
    }
    return response

@app.post("/download/")
async def save_as_file(manager:GridManager = Depends(get_manager)):
    try:
        zip_bytes = manager.serialise_to_zip()
        return StreamingResponse(
                io.BytesIO(zip_bytes),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=planning.zip"}
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed:{str(e)}")

@app.post("/upload/")
async def upload_file(request:Request, manager:GridManager = Depends(get_manager)):
    try:
        zip_bytes = await request.body()
        manager_instance = GridManager.deserialise_from_zip(zip_bytes)
        app.state.grid_manager = manager_instance
        return JSONResponse(status_code=200)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})


