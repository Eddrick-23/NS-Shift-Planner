import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from src.backend.internal.grid_manager import GridManager

# Load .env to get credentials path
load_dotenv()
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

grid_manager = GridManager()
app = FastAPI()

def get_manager():
    return grid_manager

# Request body schema
class UploadRequest(BaseModel):
    user_id: str
    project_name: str
    data: dict

@app.post("/upload/")
async def upload_data(request: UploadRequest):
    doc_id = f"{request.user_id}_{request.project_name}" #document name
    doc_ref = db.collection("projects").document(doc_id) #folder("collection") name

    # Upload or overwrite the data using .set()
    doc_ref.set({
        "user_id": request.user_id,
        "project_name": request.project_name,
        "data": request.data
    })

    return {"message": "Data uploaded successfully"}

@app.post("/grid/")
async def get_grid(day:int,manager:GridManager = Depends(get_manager)):
    
    return len(manager.all_grids)
    

