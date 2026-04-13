from sqlalchemy import create_engine, text

from config import settings
from services.rag_service import rag_service, COLLECTION_FR, COLLECTION_AR


class IngestService:
    def __init__(self):
        self.engine = create_engine(settings.postgres_url)

    async def sync_to_qdrant(self) -> dict:
        # Clear existing collections
        try:
            rag_service.qdrant.delete_collection(COLLECTION_FR)
            rag_service.qdrant.delete_collection(COLLECTION_AR)
        except Exception:
            pass
        rag_service._ensure_collections()

        chunks_fr = []
        chunks_ar = []

        # Fetch and chunk programs with related data
        with self.engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT p.id, p.title_fr, p.title_ar,
                       p.description_fr, p.description_ar,
                       p.duration_days, p.price, p.currency,
                       p.category, p.target_audience, p.includes,
                       p.start_date, p.end_date,
                       d.name_fr AS dest_fr, d.name_ar AS dest_ar,
                       d.country, d.city,
                       h.name AS hotel_name, h.stars, h.category AS hotel_cat,
                       h.price_per_night AS hotel_price
                FROM programs p
                JOIN destinations d ON p.destination_id = d.id
                LEFT JOIN hotels h ON p.hotel_id = h.id
                WHERE p.is_active = TRUE
            """)).fetchall()

            for row in rows:
                # French chunk
                includes_str = ", ".join(row.includes) if row.includes else ""
                fr_text = (
                    f"Programme: {row.title_fr}\n"
                    f"Destination: {row.dest_fr}, {row.country}\n"
                    f"Description: {row.description_fr}\n"
                    f"Durée: {row.duration_days} jours\n"
                    f"Prix: {row.price} {row.currency}\n"
                    f"Catégorie: {row.category}\n"
                    f"Public cible: {row.target_audience}\n"
                    f"Inclus: {includes_str}\n"
                    f"Hôtel: {row.hotel_name or 'N/A'} ({row.hotel_cat or 'N/A'})\n"
                    f"Dates: {row.start_date} - {row.end_date}"
                )
                chunks_fr.append({
                    "text": fr_text,
                    "type": "program",
                    "source_id": row.id,
                    "title": row.title_fr,
                    "category": row.category,
                    "target_audience": row.target_audience,
                    "destination": row.dest_fr,
                    "price": float(row.price) if row.price else 0,
                })

                # Arabic chunk
                if row.title_ar and row.description_ar:
                    ar_text = (
                        f"البرنامج: {row.title_ar}\n"
                        f"الوجهة: {row.dest_ar}, {row.country}\n"
                        f"الوصف: {row.description_ar}\n"
                        f"المدة: {row.duration_days} أيام\n"
                        f"السعر: {row.price} {row.currency}\n"
                        f"الفئة: {row.category}\n"
                        f"الجمهور المستهدف: {row.target_audience}\n"
                        f"يشمل: {includes_str}\n"
                        f"الفندق: {row.hotel_name or 'غير محدد'}\n"
                        f"التواريخ: {row.start_date} - {row.end_date}"
                    )
                    chunks_ar.append({
                        "text": ar_text,
                        "type": "program",
                        "source_id": row.id,
                        "title": row.title_ar,
                        "category": row.category,
                        "target_audience": row.target_audience,
                        "destination": row.dest_ar,
                        "price": float(row.price) if row.price else 0,
                    })

            # Fetch and chunk destinations
            dest_rows = conn.execute(text("""
                SELECT id, name_fr, name_ar, country, city,
                       description_fr, description_ar, climate,
                       best_season, visa_required
                FROM destinations
            """)).fetchall()

            for row in dest_rows:
                fr_text = (
                    f"Destination: {row.name_fr}, {row.country}\n"
                    f"Ville: {row.city}\n"
                    f"Description: {row.description_fr}\n"
                    f"Climat: {row.climate}\n"
                    f"Meilleure saison: {row.best_season}\n"
                    f"Visa requis: {'Oui' if row.visa_required else 'Non'}"
                )
                chunks_fr.append({
                    "text": fr_text,
                    "type": "destination",
                    "source_id": row.id,
                    "title": row.name_fr,
                })

                if row.name_ar and row.description_ar:
                    ar_text = (
                        f"الوجهة: {row.name_ar}, {row.country}\n"
                        f"المدينة: {row.city}\n"
                        f"الوصف: {row.description_ar}\n"
                        f"المناخ: {row.climate}\n"
                        f"أفضل موسم: {row.best_season}\n"
                        f"تأشيرة مطلوبة: {'نعم' if row.visa_required else 'لا'}"
                    )
                    chunks_ar.append({
                        "text": ar_text,
                        "type": "destination",
                        "source_id": row.id,
                        "title": row.name_ar,
                    })

            # Fetch and chunk hotels
            hotel_rows = conn.execute(text("""
                SELECT h.id, h.name, h.stars, h.price_per_night,
                       h.currency, h.amenities, h.description_fr,
                       h.description_ar, h.category, h.address,
                       d.name_fr AS dest_fr, d.name_ar AS dest_ar
                FROM hotels h
                JOIN destinations d ON h.destination_id = d.id
            """)).fetchall()

            for row in hotel_rows:
                amenities_str = ", ".join(row.amenities) if row.amenities else ""
                fr_text = (
                    f"Hôtel: {row.name}\n"
                    f"Destination: {row.dest_fr}\n"
                    f"Étoiles: {row.stars}\n"
                    f"Prix par nuit: {row.price_per_night} {row.currency}\n"
                    f"Catégorie: {row.category}\n"
                    f"Équipements: {amenities_str}\n"
                    f"Description: {row.description_fr}\n"
                    f"Adresse: {row.address}"
                )
                chunks_fr.append({
                    "text": fr_text,
                    "type": "hotel",
                    "source_id": row.id,
                    "title": row.name,
                    "category": row.category,
                    "destination": row.dest_fr,
                })

                if row.description_ar:
                    ar_text = (
                        f"الفندق: {row.name}\n"
                        f"الوجهة: {row.dest_ar}\n"
                        f"النجوم: {row.stars}\n"
                        f"السعر لليلة: {row.price_per_night} {row.currency}\n"
                        f"الفئة: {row.category}\n"
                        f"المرافق: {amenities_str}\n"
                        f"الوصف: {row.description_ar}\n"
                        f"العنوان: {row.address}"
                    )
                    chunks_ar.append({
                        "text": ar_text,
                        "type": "hotel",
                        "source_id": row.id,
                        "title": row.name,
                        "category": row.category,
                        "destination": row.dest_ar,
                    })

            # Fetch and chunk activities
            act_rows = conn.execute(text("""
                SELECT a.id, a.name_fr, a.name_ar,
                       a.description_fr, a.description_ar,
                       a.price, a.currency, a.duration_hours,
                       a.category, d.name_fr AS dest_fr, d.name_ar AS dest_ar
                FROM activities a
                JOIN destinations d ON a.destination_id = d.id
            """)).fetchall()

            for row in act_rows:
                fr_text = (
                    f"Activité: {row.name_fr}\n"
                    f"Destination: {row.dest_fr}\n"
                    f"Description: {row.description_fr}\n"
                    f"Prix: {row.price} {row.currency}\n"
                    f"Durée: {row.duration_hours} heures\n"
                    f"Catégorie: {row.category}"
                )
                chunks_fr.append({
                    "text": fr_text,
                    "type": "activity",
                    "source_id": row.id,
                    "title": row.name_fr,
                    "category": row.category,
                    "destination": row.dest_fr,
                })

                if row.name_ar and row.description_ar:
                    ar_text = (
                        f"النشاط: {row.name_ar}\n"
                        f"الوجهة: {row.dest_ar}\n"
                        f"الوصف: {row.description_ar}\n"
                        f"السعر: {row.price} {row.currency}\n"
                        f"المدة: {row.duration_hours} ساعات\n"
                        f"الفئة: {row.category}"
                    )
                    chunks_ar.append({
                        "text": ar_text,
                        "type": "activity",
                        "source_id": row.id,
                        "title": row.name_ar,
                        "category": row.category,
                        "destination": row.dest_ar,
                    })

        # Upload to Qdrant
        fr_count = await rag_service.add_chunks(chunks_fr, COLLECTION_FR)
        ar_count = await rag_service.add_chunks(chunks_ar, COLLECTION_AR)

        return {
            "status": "ok",
            "chunks_fr": fr_count,
            "chunks_ar": ar_count,
            "total": fr_count + ar_count,
        }


ingest_service = IngestService()
