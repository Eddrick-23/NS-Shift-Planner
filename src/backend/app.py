from typing import cast
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from src.backend.internal.grid_manager import GridManager, GridHandler

# Load .env to get credentials path
load_dotenv()
# cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# cred = credentials.Certificate(cred_path)
# firebase_admin.initialize_app(cred)

# # Initialize Firestore client
# db = firestore.client()

grid_manager = GridManager()
app = FastAPI()


def get_manager():
    return grid_manager


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
    handlers = {}
    day = request.day
    # find the required handlers
    for key, handler in manager.all_grids.items():
        if f"DAY{day}" not in key:
            continue
        num = len(handlers) + 1
        handlers[f"df{num}"] = handler.data

    # format the keys
    blocks_to_remove = manager.format_keys(**handlers)

    # get the formatted dataframe in aggrid format
    for key, handler in manager.all_grids.items():
        if f"DAY{day}" not in key:
            continue
        handler = cast(GridHandler, handler)
        formatted_df = handler.generate_formatted_dataframe(blocks_to_remove)
        aggrid_format = handler.df_to_aggrid_format(formatted_df)
        result[key] = aggrid_format
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.post("/grid/add/")
async def add_name(
    request: AddOrRemoveRequest, manager: GridManager = Depends(get_manager)
):
    target_grid = request.grid_name
    day = target_grid[3]
    name = request.name.upper()
    if manager.name_exists(name,day):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail":f"{name} already exists in DAY:{day}"}
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": f"Allocated: {target_grid},{name},{time_block},{allocation_size},{location}"
        },
    )
