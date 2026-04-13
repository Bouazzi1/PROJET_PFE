from fastapi import APIRouter

from api.routes import health, rag, ocr, recommend, ingest, conversations

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(rag.router, prefix="/rag", tags=["RAG"])
router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
router.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
