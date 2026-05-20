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

    # 2. Detect language
    lang = await memory_service.get_language(request.channel, request.client_id)
    if not lang and request.content:
        lang = language_service.detect(request.content)
        await memory_service.set_language(request.channel, request.client_id, lang)
    if not lang:
        lang = "fr"

    # 3. Handle passport image
    if request.has_media and request.media_url:
        intent = "ocr"
        response_text = await _handle_passport_image(request.media_url, request.client_id, lang)
        client_msg = "[Image passeport envoyée]"

    else:
        client_msg = request.content
        intent = await _classify_intent(request.content, lang)

        # 4. Route
        if intent == "recommendation":
            response_text, intent = await _handle_recommendation(
                request.content, request.channel, request.client_id, lang, history
            )

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
            # Check if we're waiting for recommendation profile info
            if await memory_service.is_awaiting_rec(request.channel, request.client_id):
                response_text, intent = await _handle_recommendation(
                    request.content, request.channel, request.client_id, lang, history
                )
            else:
                rag_result = await rag_service.query(
                    question=request.content,
                    language=lang,
                    history=history,
                )
                response_text = rag_result["answer"]

    # 5. Save to memory
    await memory_service.add_message(request.channel, request.client_id, "client", client_msg)
    await memory_service.add_message(request.channel, request.client_id, "assistant", response_text)

    return MessageResponse(
        response=response_text,
        language=lang,
        intent=intent,
        client_id=request.client_id,
    )


# ------------------------------------------------------------------
# Recommendation handler (with profile collection)
# ------------------------------------------------------------------

async def _handle_recommendation(
    content: str, channel: str, client_id: str, lang: str, history: list[dict]
) -> tuple[str, str]:
    """
    Extract profile features from message + history + Redis.
    If complete → call LightGBM recommender.
    If incomplete → ask for missing info and store state in Redis.
    """
    # Extract from current message
    extracted = _extract_profile_features(content, history)

    # Merge with previously stored partial info (Redis)
    stored = await memory_service.get_rec_profile(channel, client_id)
    profile_type      = extracted.get("profile_type")      or stored.get("profile_type")
    budget_preference = extracted.get("budget_preference") or stored.get("budget_preference")

    # Save whatever we now know
    await memory_service.set_rec_profile(channel, client_id, profile_type, budget_preference)

    missing_profile = not profile_type
    missing_budget  = not budget_preference

    if missing_profile or missing_budget:
        # Store awaiting state and ask for missing info
        await memory_service.set_awaiting_rec(channel, client_id)
        return _ask_profile_questions(lang, missing_profile, missing_budget), "recommendation_pending"

    # All info present → call LightGBM
    result = await recommendation_service.recommend(
        client_id=client_id,
        language=lang,
        preferences={"profile_type": profile_type, "budget_preference": budget_preference},
    )
    await memory_service.clear_rec_state(channel, client_id)
    return result.get("response", ""), "recommendation"


def _extract_profile_features(content: str, history: list[dict]) -> dict:
    """
    Keyword-based extraction of profile_type and budget_preference.
    Scans current message + last 6 client messages from history.
    """
    # Build text corpus: current message + recent client turns
    parts = [content.lower()]
    for msg in history[-6:]:
        if msg.get("role") == "client":
            parts.append(msg.get("content", "").lower())
    text = " ".join(parts)

    profile_type = None
    budget_preference = None

    # --- Profile type ---
    if any(kw in text for kw in ["étudiant", "etudiant", "student", "université", "universite", "faculté", "طالب"]):
        profile_type = "student"
    elif any(kw in text for kw in ["famille", "family", "enfant", "enfants", "kids", "mes enfants", "عائلة", "أطفال"]):
        profile_type = "family"
    elif any(kw in text for kw in ["couple", "ma femme", "mon mari", "lune de miel", "romantique", "زوجان", "مع زوجتي", "مع زوجي"]):
        profile_type = "couple"
    elif any(kw in text for kw in ["business", "affaires", "professionnel", "voyage d'affaires", "أعمال", "عمل"]):
        profile_type = "business"
    elif any(kw in text for kw in ["retraité", "retraite", "senior", "âgé", "كبير في السن", "متقاعد"]):
        profile_type = "senior"
    elif any(kw in text for kw in ["jeune", "young", "amis", "entre amis", "seul", "شاب", "شبان", "أصدقاء"]):
        profile_type = "young"

    # --- Budget preference ---
    if any(kw in text for kw in [
        "petit budget", "budget limité", "pas cher", "économique", "economique",
        "abordable", "pas trop cher", "budget serré", "modeste", "moins cher",
        "ميزانية محدودة", "رخيص", "اقتصادي",
    ]):
        budget_preference = "budget"
    elif any(kw in text for kw in [
        "luxe", "luxury", "premium", "haut de gamme", "première classe",
        "vip", "5 étoiles", "5 etoiles", "meilleur hôtel",
        "فاخر", "فخم", "5 نجوم", "درجة أولى",
    ]):
        budget_preference = "luxury"
    elif any(kw in text for kw in [
        "budget moyen", "standard", "modéré", "raisonnable", "correct",
        "milieu de gamme", "ni trop cher", "متوسط", "معقول",
    ]):
        budget_preference = "standard"

    return {"profile_type": profile_type, "budget_preference": budget_preference}


def _ask_profile_questions(lang: str, missing_profile: bool, missing_budget: bool) -> str:
    if lang == "ar":
        if missing_profile and missing_budget:
            return (
                "يسعدني مساعدتك في اختيار أفضل برنامج سياحي! أحتاج لمعرفة:\n\n"
                "1️⃣ *من سيسافر؟*\n"
                "   طالب | شاب | عائلة | زوجان | رجل أعمال | كبير في السن\n\n"
                "2️⃣ *ما هي ميزانيتك؟*\n"
                "   اقتصادية | متوسطة | فاخرة"
            )
        elif missing_profile:
            return (
                "لمساعدتك بشكل أفضل، من سيسافر؟\n"
                "طالب | شاب | عائلة | زوجان | رجل أعمال | كبير في السن"
            )
        else:
            return (
                "ما هي ميزانيتك التقريبية؟\n"
                "اقتصادية | متوسطة | فاخرة"
            )
    else:
        if missing_profile and missing_budget:
            return (
                "Avec plaisir ! Pour vous proposer les programmes les mieux adaptés, j'ai besoin de deux informations :\n\n"
                "1️⃣ *Qui voyage ?*\n"
                "   Étudiant | Jeune | Famille | Couple | Professionnel | Senior\n\n"
                "2️⃣ *Quel est votre budget ?*\n"
                "   Économique | Moyen | Luxe"
            )
        elif missing_profile:
            return (
                "Pour affiner ma recommandation, qui sera du voyage ?\n"
                "Étudiant | Jeune | Famille | Couple | Professionnel | Senior"
            )
        else:
            return (
                "Quel est votre budget approximatif ?\n"
                "Économique | Moyen | Luxe"
            )


# ------------------------------------------------------------------
# Passport OCR handler
# ------------------------------------------------------------------

async def _handle_passport_image(media_url: str, client_id: str, lang: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(media_url, headers={"X-Api-Key": settings.waha_api_key})
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


# ------------------------------------------------------------------
# Get conversation history
# ------------------------------------------------------------------

@router.get("/{client_id}")
async def get_conversation(client_id: str, channel: str = "whatsapp"):
    history = await memory_service.get_history(channel, client_id)
    return {"messages": history}


# ------------------------------------------------------------------
# Intent classification
# ------------------------------------------------------------------

async def _classify_intent(content: str, lang: str) -> str:
    content_lower = content.lower()

    recommendation_keywords = [
        "recommand", "suggest", "conseil", "meilleur", "proposer",
        "personnalis", "adapté", "pour moi", "quel voyage",
        "quelque chose", "selon mon profil",
        "توصية", "اقتراح", "أفضل", "انصحني", "اقترح",
    ]
    passport_keywords = [
        "passeport", "passport", "جواز", "visa",
    ]
    booking_keywords = [
        "réserv", "reserv", "book", "حجز", "inscrire",
    ]
    program_keywords = [
        "programme", "forfait", "séjour", "voyage",
        "offre", "package", "formule", "circuit", "disponible",
        "avez-vous", "proposez", "prix pour", "combien pour",
        "برنامج", "برامج", "رحلة", "عرض", "عروض", "باقة",
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
