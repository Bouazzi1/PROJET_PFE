import httpx

from config import settings


class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_model
        self.embed_model = settings.embed_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        model = model or self.model
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 1024,
            },
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate", json=payload
            )
            response.raise_for_status()
            return response.json()["response"]

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        model = model or self.embed_model
        if not text or not text.strip():
            return [0.0] * 768
        payload = {"model": model, "input": text}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embed", json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"][0]

    async def embed_batch(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        model = model or self.embed_model
        payload = {"model": model, "input": texts}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embed", json=payload
            )
            response.raise_for_status()
            return response.json()["embeddings"]


llm_service = LLMService()
