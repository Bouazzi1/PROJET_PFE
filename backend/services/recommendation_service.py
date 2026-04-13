from sqlalchemy import create_engine, text

from config import settings
from services.llm_service import llm_service


# Profile → category mapping
PROFILE_CATEGORY_MAP = {
    "student": {"preferred": "budget", "activities": ["adventure", "cultural", "nightlife"]},
    "business": {"preferred": "luxury", "activities": ["relaxation", "cultural"]},
    "family": {"preferred": "standard", "activities": ["cultural", "relaxation"]},
    "young": {"preferred": "budget", "activities": ["adventure", "nightlife", "shopping"]},
    "senior": {"preferred": "luxury", "activities": ["relaxation", "religious", "cultural"]},
    "couple": {"preferred": "luxury", "activities": ["relaxation", "adventure"]},
}


class RecommendationService:
    def __init__(self):
        self.engine = create_engine(settings.postgres_url)

    async def recommend(
        self,
        client_id: str,
        preferences: dict | None = None,
        destination: str | None = None,
        language: str = "fr",
    ) -> dict:
        # 1. Get client profile
        profile = self._get_client_profile(client_id)
        profile_type = profile.get("profile_type", "unknown")
        budget_pref = profile.get("budget_preference", "unknown")

        # Use preferences if provided
        if preferences:
            profile_type = preferences.get("profile_type", profile_type)
            budget_pref = preferences.get("budget", budget_pref)

        # 2. Get active programs
        programs = self._get_programs(destination)

        if not programs:
            no_result = "لا توجد برامج متاحة حالياً." if language == "ar" else "Aucun programme disponible actuellement."
            return {"response": no_result, "recommendations": []}

        # 3. Score programs
        scored = []
        for prog in programs:
            score = self._score_program(prog, profile_type, budget_pref)
            scored.append({"program": prog, "score": score})

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:3]

        # 4. Generate natural language recommendations via LLM
        response_text = await self._generate_recommendation_text(
            top, profile_type, budget_pref, language
        )

        return {
            "response": response_text,
            "recommendations": [
                {
                    "program_id": r["program"]["id"],
                    "title": r["program"]["title_fr"] if language == "fr" else r["program"].get("title_ar", r["program"]["title_fr"]),
                    "score": r["score"],
                    "price": r["program"]["price"],
                }
                for r in top
            ],
        }

    def _get_client_profile(self, client_id: str) -> dict:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("SELECT profile_type, budget_preference FROM clients WHERE phone = :phone OR email = :email"),
                {"phone": client_id, "email": client_id},
            ).fetchone()
            if row:
                return {
                    "profile_type": row.profile_type or "unknown",
                    "budget_preference": row.budget_preference or "unknown",
                }
        return {"profile_type": "unknown", "budget_preference": "unknown"}

    def _get_programs(self, destination: str | None = None) -> list[dict]:
        query = """
            SELECT p.id, p.title_fr, p.title_ar, p.description_fr, p.description_ar,
                   p.duration_days, p.price, p.currency, p.category,
                   p.target_audience, p.includes, p.start_date, p.end_date,
                   d.name_fr AS dest_fr, d.name_ar AS dest_ar
            FROM programs p
            JOIN destinations d ON p.destination_id = d.id
            WHERE p.is_active = TRUE
        """
        params = {}
        if destination:
            query += " AND (LOWER(d.name_fr) LIKE :dest OR LOWER(d.name_ar) LIKE :dest)"
            params["dest"] = f"%{destination.lower()}%"

        with self.engine.connect() as conn:
            rows = conn.execute(text(query), params).fetchall()
            return [
                {
                    "id": r.id,
                    "title_fr": r.title_fr,
                    "title_ar": r.title_ar,
                    "description_fr": r.description_fr,
                    "description_ar": r.description_ar,
                    "duration_days": r.duration_days,
                    "price": float(r.price) if r.price else 0,
                    "currency": r.currency,
                    "category": r.category,
                    "target_audience": r.target_audience,
                    "includes": r.includes or [],
                    "dest_fr": r.dest_fr,
                    "dest_ar": r.dest_ar,
                }
                for r in rows
            ]

    def _score_program(
        self, program: dict, profile_type: str, budget_pref: str
    ) -> float:
        score = 0.0
        mapping = PROFILE_CATEGORY_MAP.get(profile_type, {})

        # Budget match (+30)
        preferred_budget = mapping.get("preferred", budget_pref)
        if program["category"] == preferred_budget:
            score += 30
        elif program["category"] == "standard":
            score += 15  # standard is always acceptable

        # Audience match (+25)
        if program["target_audience"] == profile_type:
            score += 25
        elif program["target_audience"] == "all":
            score += 15

        # Price factor (+20 max)
        price = program["price"]
        if preferred_budget == "budget" and price < 100000:
            score += 20
        elif preferred_budget == "standard" and 80000 <= price <= 200000:
            score += 20
        elif preferred_budget == "luxury" and price > 150000:
            score += 20

        # Base relevance
        score += 10

        return round(score, 1)

    async def _generate_recommendation_text(
        self,
        recommendations: list[dict],
        profile_type: str,
        budget_pref: str,
        language: str,
    ) -> str:
        programs_text = ""
        for i, rec in enumerate(recommendations, 1):
            prog = rec["program"]
            title = prog["title_fr"] if language == "fr" else prog.get("title_ar", prog["title_fr"])
            dest = prog["dest_fr"] if language == "fr" else prog.get("dest_ar", prog["dest_fr"])
            desc = prog["description_fr"] if language == "fr" else prog.get("description_ar", prog["description_fr"])
            programs_text += (
                f"{i}. {title} - {dest}\n"
                f"   Prix: {prog['price']} {prog['currency']}, "
                f"Durée: {prog['duration_days']} jours\n"
                f"   {desc}\n\n"
            )

        if language == "ar":
            prompt = (
                f"أنت مستشار سفر. بناءً على ملف العميل ({profile_type}, ميزانية {budget_pref})، "
                f"اقترح هذه البرامج بطريقة شخصية ومقنعة. اشرح لماذا كل برنامج مناسب لهذا العميل.\n\n"
                f"البرامج:\n{programs_text}\n"
                f"الاقتراح:"
            )
        else:
            prompt = (
                f"Tu es un conseiller voyage. En fonction du profil client ({profile_type}, budget {budget_pref}), "
                f"propose ces programmes de manière personnalisée et convaincante. Explique pourquoi chaque programme convient à ce client.\n\n"
                f"Programmes:\n{programs_text}\n"
                f"Recommandation:"
            )

        return await llm_service.generate(prompt=prompt, temperature=0.5)


recommendation_service = RecommendationService()
