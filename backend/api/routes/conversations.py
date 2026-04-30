import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from services.memory_service import memory_service
from services.language_service import language_service
from services.rag_service import rag_service
from services.recommendation_service import recommendation_service
from services.ocr_service import ocr_service
from config import settings

router = APIRouter()


class MessageRequest(BaseModel):
    client_id: str
    channel: str = "whatsapp"
    content: str = ""
    media_url: str | None = None
    has_media: bool = False


class MessageResponse(BaseModel):
    response: str
    language: str = "fr"
    intent: str = "general"
    client_id: str = ""


@router.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    # 1. Load conversation history
    history = await memory_service.get_history(request.channel, request.client_id)

    # 2. Detect language (only on first message)
    lang = await memory_service.get_language(request.channel, request.client_id)
    if not lang and request.content:
        lang = language_service.detect(request.content)
        await memory_service.set_language(request.channel, request.client_id, lang)
    if not lang:
        lang = "fr"

    # 3. Handle image (passport OCR)
    if request.has_media and request.media_url:
        intent = "ocr"
        response_text = await _handle_passport_image(
            request.media_url, request.client_id, lang
        )
        client_msg = "[Image passeport envoyée]"
    else:
        client_msg = request.content
        # 4. Classify intent
        intent = await _classify_intent(request.content, lang)

        # 5. Route to appropriate handler
        if intent == "recommendation":
            result = await recommendation_service.recommend(
                client_id=request.client_id,
                language=lang,
            )
            response_text = result.get("response", "")
        elif intent == "passport":
            response_text = _passport_instructions(lang)
        elif intent == "booking":
            response_text = _booking_instructions(lang)
        elif intent == "program":
            rag_result = await rag_service.query(
                question=request.content,
                language=lang,
                history=history,
                filter_type="program",
                top_k=20,
            )
            response_text = rag_result["answer"]
        else:
            rag_result = await rag_service.query(
                question=request.content,
                language=lang,
                history=history,
            )
            response_text = rag_result["answer"]

    # 6. Save to memory
    await memory_service.add_message(
        request.channel, request.client_id, "client", client_msg
    )
    await memory_service.add_message(
        request.channel, request.client_id, "assistant", response_text
    )

    return MessageResponse(
        response=response_text,
        language=lang,
        intent=intent,
        client_id=request.client_id,
    )


async def _handle_passport_image(media_url: str, client_id: str, lang: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(
                media_url,
                headers={"X-Api-Key": settings.waha_api_key},
            )
            image_bytes = resp.content

        result = await ocr_service.extract_passport(image_bytes, client_id)
        pp = result.get("passport_data", {})

        if lang == "ar":
            return (
                f"تم استلام جواز السفر! إليك المعلومات المستخرجة:\n\n"
                f"الاسم العائلي: {pp.get('surname') or 'غير متوفر'}\n"
                f"الأسماء: {pp.get('given_names') or 'غير متوفر'}\n"
                f"رقم الجواز: {pp.get('passport_number') or 'غير متوفر'}\n"
                f"الجنسية: {pp.get('nationality') or 'غير متوفر'}\n"
                f"تاريخ الانتهاء: {pp.get('date_of_expiry') or 'غير متوفر'}"
            )
        return (
            f"Passeport reçu ! Voici les informations extraites :\n\n"
            f"Nom : {pp.get('surname') or 'N/A'}\n"
            f"Prénoms : {pp.get('given_names') or 'N/A'}\n"
            f"N° Passeport : {pp.get('passport_number') or 'N/A'}\n"
            f"Nationalité : {pp.get('nationality') or 'N/A'}\n"
            f"Date d'expiration : {pp.get('date_of_expiry') or 'N/A'}"
        )
    except Exception:
        if lang == "ar":
            return "عذراً، لم أتمكن من قراءة هذا المستند. يرجى إرسال صورة أوضح."
        return "Désolé, je n'ai pas pu lire ce document. Veuillez envoyer une photo plus claire."


@router.get("/{client_id}")
async def get_conversation(client_id: str, channel: str = "whatsapp"):
    history = await memory_service.get_history(channel, client_id)
    return {"messages": history}


async def _classify_intent(content: str, lang: str) -> str:
    content_lower = content.lower()

    recommendation_keywords = [
        "recommand", "suggest", "conseil", "meilleur", "proposer",
        "personnalis", "adapté", "توصية", "اقتراح", "أفضل",
    ]
    passport_keywords = [
        "passeport", "passport", "جواز", "visa",
    ]
    booking_keywords = [
        "réserv", "reserv", "book", "حجز", "inscrire",
    ]
    program_keywords = [
        "programme", "programs", "forfait", "séjour", "voyage",
        "offre", "package", "formule", "circuit", "disponible",
        "avez-vous", "proposez", "prix pour", "combien pour",
        "برنامج", "برامج", "رحلة", "عرض", "باقة",
    ]

    for kw in recommendation_keywords:
        if kw in content_lower:
            return "recommendation"
    for kw in passport_keywords:
        if kw in content_lower:
            return "passport"
    for kw in booking_keywords:
        if kw in content_lower:
            return "booking"
    for kw in program_keywords:
        if kw in content_lower:
            return "program"
    return "general"


def _passport_instructions(lang: str) -> str:
    if lang == "ar":
        return "يرجى إرسال صورة جواز سفرك وسأقوم باستخراج المعلومات اللازمة تلقائياً."
    return "Veuillez envoyer une photo de votre passeport et j'extrairai automatiquement les informations nécessaires."


def _booking_instructions(lang: str) -> str:
    if lang == "ar":
        return "لإتمام الحجز، أحتاج إلى: اسمك الكامل، رقم هاتفك، وصورة جواز سفرك. هل يمكنك إرسال هذه المعلومات؟"
    return "Pour finaliser la réservation, j'ai besoin de : votre nom complet, votre numéro de téléphone, et une photo de votre passeport. Pouvez-vous m'envoyer ces informations ?"
