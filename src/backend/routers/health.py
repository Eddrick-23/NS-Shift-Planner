from fastapi import APIRouter
from src.backend.config import config

router = APIRouter()

@router.get("/health/")
async def health_check():
    return {"status": "ok"}


@router.get("/")
async def root():
    return {"name": "nsplanner API", "version": config.VERSION, "status": "running"}
