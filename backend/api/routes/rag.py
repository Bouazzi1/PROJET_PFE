from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import rag_service

router = APIRouter()


class RAGQuery(BaseModel):
    question: str
    client_id: str | None = None
    channel: str | None = None
    language: str | None = None


class RAGResponse(BaseModel):
    answer: str
    sources: list[dict] = []
    language: str = "fr"


@router.post("/query", response_model=RAGResponse)
async def query_rag(query: RAGQuery):
    result = await rag_service.query(
        question=query.question,
        language=query.language,
    )
    return result
