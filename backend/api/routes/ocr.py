from fastapi import APIRouter, UploadFile, File, Form

from services.ocr_service import ocr_service

router = APIRouter()


@router.post("/passport")
async def process_passport(
    file: UploadFile = File(...),
    client_id: str | None = Form(None),
):
    image_bytes = await file.read()
    result = await ocr_service.extract_passport(image_bytes, client_id)
    return result
