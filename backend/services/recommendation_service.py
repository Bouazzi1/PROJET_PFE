from pathlib import Path

from sqlalchemy import create_engine, text

from config import settings
from services.llm_service import llm_service

# --- Model path (resolves to /app/recommender/models/ in Docker) ---
_MODEL_PATH = Path(__file__).parent.parent / "recommender" / "models" / "lightgbm_recommender.joblib"

# --- Value mappings: DB values → model expected values (English) ---
PROFILE_TYPE_MAP = {
    "student": "student", "étudiant": "student", "etudiant": "student",
    "young": "young", "jeune": "young",
    "family": "family", "famille": "family",
    "couple": "couple",
    "business": "business", "affaires": "business",
    "senior": "senior",
}

BUDGET_MAP = {
    "budget": "budget", "économique": "budget", "economique": "budget",
    "standard": "standard", "moyen": "standard",
    "luxury": "luxury", "luxe": "luxury", "premium": "luxury",
}


def _load_recommender():
    try:
        from recommender.src.predictor import TravelRecommender
        if _MODEL_PATH.exists():
            rec = TravelRecommender(str(_MODEL_PATH))
            print(f"[RecommendationService] LightGBM chargé depuis {_MODEL_PATH}")
            return rec
        print(f"[RecommendationService] Modèle introuvable : {_MODEL_PATH}")
    except Exception as e:
        print(f"[RecommendationService] Erreur chargement LightGBM : {e}")
    return None


class RecommendationService:
    def __init__(self):
        self.engine = create_engine(settings.postgres_url)
        self._recommender = _load_recommender()

    async def recommend(
        self,
        client_id: str,
        preferences: dict | None = None,
        destination: str | None = None,
        language: str = "fr",
    ) -> dict:
        # 1. Client profile from PostgreSQL
        profile = self._get_client_profile(client_id, language)

        # 2. Override with preferences extracted from conversation
        if preferences:
            if preferences.get("profile_type"):
                mapped = PROFILE_TYPE_MAP.get(preferences["profile_type"])
                if mapped:
                    profile["profile_type"] = mapped
            if preferences.get("budget_preference"):
                mapped = BUDGET_MAP.get(preferences["budget_preference"])
                if mapped:
                    profile["budget_preference"] = mapped

        # 3. Load programs with full JOIN (programs + destinations + hotels)
        programs = self._get_programs(destination)
        if not programs:
            msg = "لا توجد برامج متاحة حالياً." if language == "ar" else "Aucun programme disponible actuellement."
            return {"response": msg, "recommendations": []}

        # 4. Rank with LightGBM (fallback: rule-based)
        ranked = self._rank_programs(profile, programs, language)
        top = ranked[:3]

        # 5. LLM generates natural language explanation
        response_text = await self._generate_response(top, profile, language)

        # 6. Persist recommendations to PostgreSQL
        db_client_id = profile.get("db_id")
        if db_client_id:
            self._save_recommendations(db_client_id, top, response_text)

        return {
            "response": response_text,
            "recommendations": [
                {
                    "program_id": r["id"],
                    "title": r["title_fr"] if language == "fr" else r.get("title_ar") or r["title_fr"],
                    "score": r.get("score", 0.0),
                    "price": r["price"],
                    "currency": r.get("currency", "TND"),
                }
                for r in top
            ],
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_client_profile(self, client_id: str, language: str = "fr") -> dict:
        with self.engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT id, profile_type, budget_preference, preferred_language "
                    "FROM clients WHERE phone = :id OR email = :id"
                ),
                {"id": client_id},
            ).fetchone()
            if row:
                return {
                    "db_id": row.id,
                    "profile_type": PROFILE_TYPE_MAP.get(row.profile_type or "", "young"),
                    "budget_preference": BUDGET_MAP.get(row.budget_preference or "", "standard"),
                    "preferred_language": row.preferred_language or language,
                }
        return {"db_id": None, "profile_type": "young", "budget_preference": "standard", "preferred_language": language}

    def _save_recommendations(self, client_db_id: int, top: list[dict], llm_reason: str) -> None:
        try:
            with self.engine.begin() as conn:
                # Remove previous unseen recommendations for this client
                conn.execute(
                    text("DELETE FROM recommendations WHERE client_id = :cid AND was_accepted IS NULL"),
                    {"cid": client_db_id},
                )
                for rank, prog in enumerate(top, 1):
                    conn.execute(
                        text("""
                            INSERT INTO recommendations (client_id, program_id, score, reason, was_accepted)
                            VALUES (:cid, :pid, :score, :reason, NULL)
                        """),
                        {
                            "cid": client_db_id,
                            "pid": prog["id"],
                            "score": round(prog.get("score", 0.0), 3),
                            "reason": f"#{rank} — {llm_reason[:300]}" if rank == 1 else f"#{rank}",
                        },
                    )
        except Exception as e:
            print(f"[RecommendationService] Erreur sauvegarde recommendations : {e}")

    def _get_programs(self, destination: str | None = None) -> list[dict]:
        query = """
            SELECT
                p.id,
                p.title_fr,  p.title_ar,
                p.description_fr, p.description_ar,
                p.duration_days, p.price, p.currency,
                p.category, p.target_audience, p.includes,
                d.name_fr  AS dest_fr,  d.name_ar  AS dest_ar,
                d.climate, d.best_season, d.visa_required,
                h.stars    AS hotel_stars,
                h.amenities
            FROM programs p
            JOIN destinations d ON p.destination_id = d.id
            LEFT JOIN hotels   h ON p.hotel_id      = h.id
            WHERE p.is_active = TRUE
        """
        params: dict = {}
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
                    "price": float(r.price or 0),
                    "duration_days": int(r.duration_days or 7),
                    "currency": r.currency or "TND",
                    "category": r.category or "standard",
                    "target_audience": r.target_audience or "all",
                    "visa_required": bool(r.visa_required),
                    "hotel_stars": int(r.hotel_stars or 3),
                    "climate": r.climate or "Méditerranéen",
                    "best_season": r.best_season or "Toute l'année",
                    "amenities": list(r.amenities or []),
                    "includes": list(r.includes or []),
                    "dest_fr": r.dest_fr,
                    "dest_ar": r.dest_ar,
                }
                for r in rows
            ]

    def _rank_programs(self, profile: dict, programs: list[dict], language: str) -> list[dict]:
        client_dict = {
            "profile_type": profile.get("profile_type", "young"),
            "budget_preference": profile.get("budget_preference", "standard"),
            "preferred_language": language,
        }

        if self._recommender:
            try:
                return self._recommender.predict(client_dict, programs)
            except Exception as e:
                print(f"[RecommendationService] Erreur LightGBM predict : {e}")

        # Fallback: rule-based scoring
        return self._rule_based_rank(client_dict, programs)

    @staticmethod
    def _rule_based_rank(client: dict, programs: list[dict]) -> list[dict]:
        budget_order = {"budget": 0, "standard": 1, "luxury": 2}
        profile = client.get("profile_type", "young")
        pref = client.get("budget_preference", "standard")

        scored = []
        for p in programs:
            s = 0.0
            if p.get("target_audience") in (profile, "all"):
                s += 0.30
            if p.get("category") == pref:
                s += 0.25
            elif abs(budget_order.get(p.get("category", "standard"), 1) - budget_order.get(pref, 1)) == 1:
                s += 0.10
            if not p.get("visa_required"):
                s += 0.10
            item = dict(p)
            item["score"] = round(s, 4)
            scored.append(item)

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    async def _generate_response(
        self, programs: list[dict], profile: dict, language: str
    ) -> str:
        profile_type = profile.get("profile_type", "young")
        budget_pref = profile.get("budget_preference", "standard")

        lines = ""
        for i, p in enumerate(programs, 1):
            title = p["title_fr"] if language == "fr" else (p.get("title_ar") or p["title_fr"])
            dest = p["dest_fr"] if language == "fr" else (p.get("dest_ar") or p["dest_fr"])
            score_pct = int(p.get("score", 0) * 100)
            includes_preview = ", ".join((p.get("includes") or [])[:4])
            lines += (
                f"{i}. {title} — {dest}\n"
                f"   Prix : {p['price']:.0f} TND | {p['duration_days']} jours | Compatibilité : {score_pct}%\n"
                f"   Inclus : {includes_preview}\n\n"
            )

        if language == "ar":
            prompt = (
                f"أنت مستشار سفر محترف. العميل من نوع ({profile_type}، ميزانية {budget_pref}).\n"
                f"قدّم هذه البرامج بأسلوب شخصي ومقنع، واشرح لماذا كل برنامج مناسب لهذا العميل تحديداً.\n\n"
                f"البرامج المقترحة:\n{lines}الاقتراح:"
            )
        else:
            prompt = (
                f"Tu es un conseiller voyage professionnel. Le client est de profil ({profile_type}, budget {budget_pref}).\n"
                f"Présente ces programmes de façon personnalisée et convaincante, "
                f"en expliquant pourquoi chaque programme correspond à ce profil spécifiquement.\n\n"
                f"Programmes recommandés:\n{lines}Recommandation:"
            )

        return await llm_service.generate(prompt=prompt, temperature=0.5)


recommendation_service = RecommendationService()
