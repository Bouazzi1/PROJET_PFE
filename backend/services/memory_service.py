import json

import redis.asyncio as redis

from config import settings

HISTORY_MAX = 20
HISTORY_TTL = 86400  # 24 hours


class MemoryService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    def _key(self, channel: str, client_id: str, suffix: str) -> str:
        return f"conv:{channel}:{client_id}:{suffix}"

    async def get_history(
        self, channel: str, client_id: str
    ) -> list[dict]:
        key = self._key(channel, client_id, "messages")
        raw = await self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in raw]

    async def add_message(
        self, channel: str, client_id: str, role: str, content: str
    ):
        key = self._key(channel, client_id, "messages")
        msg = json.dumps({"role": role, "content": content})
        await self.redis.rpush(key, msg)
        await self.redis.ltrim(key, -HISTORY_MAX, -1)
        await self.redis.expire(key, HISTORY_TTL)

    async def get_language(self, channel: str, client_id: str) -> str | None:
        key = self._key(channel, client_id, "metadata")
        return await self.redis.hget(key, "language")

    async def set_language(self, channel: str, client_id: str, lang: str):
        key = self._key(channel, client_id, "metadata")
        await self.redis.hset(key, "language", lang)
        await self.redis.expire(key, HISTORY_TTL)

    async def get_context(self, channel: str, client_id: str) -> str | None:
        key = self._key(channel, client_id, "context")
        return await self.redis.get(key)

    async def set_context(self, channel: str, client_id: str, context: str):
        key = self._key(channel, client_id, "context")
        await self.redis.set(key, context, ex=HISTORY_TTL)

    async def clear(self, channel: str, client_id: str):
        keys = [
            self._key(channel, client_id, "messages"),
            self._key(channel, client_id, "metadata"),
            self._key(channel, client_id, "context"),
        ]
        await self.redis.delete(*keys)


memory_service = MemoryService()
