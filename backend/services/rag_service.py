from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid

from config import settings
from services.llm_service import llm_service

COLLECTION_FR = "rihla_fr"
COLLECTION_AR = "rihla_ar"
VECTOR_SIZE = 768  # nomic-embed-text dimension


class RAGService:
    def __init__(self):
        self.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self._ensure_collections()

    def _ensure_collections(self):
        for name in [COLLECTION_FR, COLLECTION_AR]:
            try:
                self.qdrant.get_collection(name)
            except Exception:
                self.qdrant.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE, distance=Distance.COSINE
                    ),
                )

    async def query(
        self,
        question: str,
        language: str | None = None,
        history: list[dict] | None = None,
        top_k: int = 5,
        filter_type: str | None = None,
    ) -> dict:
        language = language or "fr"
        collection = COLLECTION_FR if language == "fr" else COLLECTION_AR

        # Build contextual query from history
        contextual_query = question
        if history and len(history) > 0:
            recent = history[-4:]  # last 2 exchanges
            context_parts = [f"{m['role']}: {m['content']}" for m in recent]
            contextual_query = "\n".join(context_parts) + f"\nclient: {question}"

        # Embed the question
        query_vector = await llm_service.embed(contextual_query)

        # Build optional filter
        qdrant_filter = None
        if filter_type:
            qdrant_filter = Filter(
                must=[FieldCondition(key="type", match=MatchValue(value=filter_type))]
            )

        # Search Qdrant
        results = self.qdrant.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        # Build context from results
        chunks = []
        sources = []
        for r in results:
            chunks.append(r.payload.get("text", ""))
            sources.append({
                "type": r.payload.get("type", ""),
                "id": r.payload.get("source_id", ""),
                "title": r.payload.get("title", ""),
                "score": round(r.score, 3),
            })

        context_text = "\n---\n".join(chunks)

        # Build history text
        history_text = ""
        if history:
            recent = history[-6:]
            history_text = "\n".join(
                [f"{'Client' if m['role']=='client' else 'Assistant'}: {m['content']}" for m in recent]
            )

        # Load prompt template
        system_prompt = self._get_system_prompt(language)
        rag_prompt = self._build_rag_prompt(context_text, history_text, question, language)

        # Generate answer
        answer = await llm_service.generate(
            prompt=rag_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        return {"answer": answer.strip(), "sources": sources, "language": language}

    def _get_system_prompt(self, lang: str) -> str:
        if lang == "ar":
            return (
                "أنت رحلة، المساعد الذكي لوكالة السفر. "
                "تساعد العملاء في إيجاد برامج السفر المناسبة لاحتياجاتهم. "
                "أجب دائماً بالعربية. كن محترفاً ودوداً ومختصراً. "
                "أجب فقط بناءً على المعلومات المتوفرة. "
                "إذا لم تجد المعلومة، قل ذلك بصراحة."
            )
        return (
            "Tu es Rihla, l'assistant intelligent de l'agence de voyage. "
            "Tu aides les clients à trouver des programmes de voyage adaptés à leurs besoins. "
            "Réponds toujours en français. Sois professionnel, chaleureux et concis. "
            "Réponds uniquement en te basant sur les informations fournies dans le contexte. "
            "Si tu ne trouves pas l'information, dis-le honnêtement."
        )

    def _build_rag_prompt(
        self, context: str, history: str, question: str, lang: str
    ) -> str:
        if lang == "ar":
            prompt = "بناءً على المعلومات التالية فقط، أجب على سؤال العميل.\n\n"
            prompt += f"المعلومات المتوفرة:\n{context}\n\n"
            if history:
                prompt += f"سجل المحادثة:\n{history}\n\n"
            prompt += f"سؤال العميل: {question}\n\nالإجابة:"
        else:
            prompt = "En te basant UNIQUEMENT sur les informations suivantes, réponds à la question du client.\n\n"
            prompt += f"Informations disponibles:\n{context}\n\n"
            if history:
                prompt += f"Historique de conversation:\n{history}\n\n"
            prompt += f"Question du client: {question}\n\nRéponse:"
        return prompt

    async def add_chunks(
        self, chunks: list[dict], collection: str = COLLECTION_FR
    ) -> int:
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        vectors = await llm_service.embed_batch(texts)

        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=chunk,
                )
            )

        self.qdrant.upsert(collection_name=collection, points=points)
        return len(points)


rag_service = RAGService()
