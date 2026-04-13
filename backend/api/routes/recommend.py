from fastapi import APIRouter
from pydantic import BaseModel

from services.recommendation_service import recommendation_service

router = APIRouter()


class RecommendRequest(BaseModel):
    client_id: str
    preferences: dict | None = None
    destination: str | None = None
    language: str = "fr"


@router.post("")
async def get_recommendations(request: RecommendRequest):
    result = await recommendation_service.recommend(
        client_id=request.client_id,
        preferences=request.preferences,
        destination=request.destination,
        language=request.language,
    )
    return result
