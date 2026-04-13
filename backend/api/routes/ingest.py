from fastapi import APIRouter

from services.ingest_service import ingest_service

router = APIRouter()


@router.post("/sync")
async def sync_data():
    result = await ingest_service.sync_to_qdrant()
    return result
