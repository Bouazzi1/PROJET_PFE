import httpx
from fastapi import APIRouter, Request

from services.memory_service import memory_service
from services.language_service import language_service
from services.rag_service import rag_service
from services.recommendation_service import recommendation_service
from services.ocr_service import ocr_service

router = APIRouter()

WAHA_API_URL = "http://host.docker.internal:3000"
WAHA_API_KEY = "rihla2026"


async def _send_whatsapp(chat_id: str, text: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(
            f"{WAHA_API_URL}/api/sendText",
            json={"chatId": chat_id, "text": text, "session": "default"},
            headers={"X-Api-Key": WAHA_API_KEY},
        )


async def _classify_intent(content: str) -> str:
    content_lower = content.lower()
    for kw in ["recommand", "suggest", "conseil", "meilleur", "proposer", "personnalis", "adapté", "توصية", "اقتراح", "أفضل"]:
        if kw in content_lower:
            return "recommendation"
    for kw in ["passeport", "passport", "جواز"]:
        if kw in content_lower:
            return "passport"
    for kw in ["réserv", "reserv", "book", "حجز", "inscrire"]:
        if kw in content_lower:
            return "booking"
    return "general"


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    body = await request.json()

    # Extract message info from WAHA payload
    event = body.get("event", "")
    payload = body.get("payload", {})

    # Only process incoming messages (not our own)
    if event != "message" or payload.get("fromMe", True):
        return {"status": "ignored"}

    chat_id = payload.get("from", "")
    message_body = payload.get("body", "")
    has_media = payload.get("hasMedia", False)

    if not chat_id or (not message_body and not has_media):
        return {"status": "no_content"}

    # Handle image (passport OCR)
    if has_media:
        try:
            # Download media from WAHA
            media_url = payload.get("mediaUrl", "")
            if media_url:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    media_resp = await client.get(
                        media_url,
                        headers={"X-Api-Key": WAHA_API_KEY},
                    )
                    image_bytes = media_resp.content

                result = await ocr_service.extract_passport(image_bytes, chat_id)
                pp = result.get("passport_data", {})
                reply = (
                    f"Passeport reçu ! Voici les informations extraites :\n\n"
                    f"Nom : {pp.get('surname') or 'N/A'}\n"
                    f"Prénoms : {pp.get('given_names') or 'N/A'}\n"
                    f"N° Passeport : {pp.get('passport_number') or 'N/A'}\n"
                    f"Nationalité : {pp.get('nationality') or 'N/A'}\n"
                    f"Date d'expiration : {pp.get('date_of_expiry') or 'N/A'}"
                )
            else:
                reply = "Veuillez envoyer une photo de votre passeport."
        except Exception as e:
            reply = f"Désolé, je n'ai pas pu lire ce document. Veuillez envoyer une photo plus claire."
        await _send_whatsapp(chat_id, reply)
        return {"status": "ok", "type": "ocr"}

    # Handle text message
    # 1. Get/detect language
    lang = await memory_service.get_language("whatsapp", chat_id)
    if not lang:
        lang = language_service.detect(message_body)
        await memory_service.set_language("whatsapp", chat_id, lang)

    # 2. Get conversation history
    history = await memory_service.get_history("whatsapp", chat_id)

    # 3. Classify intent
    intent = await _classify_intent(message_body)

    # 4. Generate response
    if intent == "recommendation":
        result = await recommendation_service.recommend(
            client_id=chat_id, language=lang,
        )
        reply = result.get("response", "Aucune recommandation disponible.")
    elif intent == "passport":
        reply = "يرجى إرسال صورة جواز سفرك." if lang == "ar" else "Veuillez envoyer une photo de votre passeport et j'extrairai les informations automatiquement."
    elif intent == "booking":
        reply = ("لإتمام الحجز، أحتاج إلى اسمك الكامل وصورة جواز سفرك." if lang == "ar"
                 else "Pour finaliser la réservation, j'ai besoin de votre nom complet et une photo de votre passeport.")
    else:
        rag_result = await rag_service.query(
            question=message_body, language=lang, history=history,
        )
        reply = rag_result["answer"]

    # 5. Save to memory
    await memory_service.add_message("whatsapp", chat_id, "client", message_body)
    await memory_service.add_message("whatsapp", chat_id, "assistant", reply)

    # 6. Send reply
    await _send_whatsapp(chat_id, reply)

    return {"status": "ok", "intent": intent, "language": lang}
