"""
All api endpoint routes
"""
from src.frontend.config import config

SESSION_ID_KEY = "session_id"

SOURCE_CODE_URL = "https://github.com/Eddrick-23/NS-Shift-Planner"
 
API_BASE = f"http://{config.HOST_NAME}:{config.BACKEND_PORT}/"

ENDPOINTS = {
    "SESSION_EXISTS": f"{API_BASE}/session_exists",
    "DOWNLOAD":f"{API_BASE}/download/",
    "UPLOAD":f"{API_BASE}/upload/",
    "RESET": f"{API_BASE}/reset-all/",
    "ADD_NAME":f"{API_BASE}/grid/add/",
    "REMOVE_NAME":f"{API_BASE}/grid/remove/",
    "FETCH_GRID":f"{API_BASE}/grid/",
    "FETCH_GRID_COMPRESSED":f"{API_BASE}/grid/compressed/",
    "ALLOCATE_SHIFT":f"{API_BASE}/grid/allocate/",
    "HOUR_DATA":f"{API_BASE}/hours/",
    "GRID_NAMES":f"{API_BASE}/grid/names/",
    "SWAP_NAMES":f"{API_BASE}/grid/swap-names/"

}
