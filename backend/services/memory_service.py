import json

import redis.asyncio as redis

from config import settings

HISTORY_MAX = 20
HISTORY_TTL = 86400  # 24 hours
REC_TTL     = 600    # 10 minutes for pending recommendation state


class MemoryService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    def _key(self, channel: str, client_id: str, suffix: str) -> str:
        return f"conv:{channel}:{client_id}:{suffix}"

    async def get_history(self, channel: str, client_id: str) -> list[dict]:
        key = self._key(channel, client_id, "messages")
        raw = await self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in raw]

    async def add_message(self, channel: str, client_id: str, role: str, content: str):
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

    # ------------------------------------------------------------------
    # Recommendation pending state
    # ------------------------------------------------------------------

    async def is_awaiting_rec(self, channel: str, client_id: str) -> bool:
        key = self._key(channel, client_id, "metadata")
        return await self.redis.hget(key, "awaiting_rec") == "1"

    async def set_awaiting_rec(self, channel: str, client_id: str):
        key = self._key(channel, client_id, "metadata")
        await self.redis.hset(key, "awaiting_rec", "1")
        await self.redis.expire(key, REC_TTL)

    async def get_rec_profile(self, channel: str, client_id: str) -> dict:
        key = self._key(channel, client_id, "metadata")
        profile_type     = await self.redis.hget(key, "rec_profile")
        budget_preference = await self.redis.hget(key, "rec_budget")
        return {"profile_type": profile_type, "budget_preference": budget_preference}

    async def set_rec_profile(
        self, channel: str, client_id: str,
        profile_type: str | None = None,
        budget_preference: str | None = None,
    ):
        key = self._key(channel, client_id, "metadata")
        if profile_type:
            await self.redis.hset(key, "rec_profile", profile_type)
        if budget_preference:
            await self.redis.hset(key, "rec_budget", budget_preference)
        await self.redis.expire(key, REC_TTL)

    async def clear_rec_state(self, channel: str, client_id: str):
        key = self._key(channel, client_id, "metadata")
        await self.redis.hdel(key, "awaiting_rec", "rec_profile", "rec_budget")

    async def clear(self, channel: str, client_id: str):
        keys = [
            self._key(channel, client_id, "messages"),
            self._key(channel, client_id, "metadata"),
            self._key(channel, client_id, "context"),
        ]
        await self.redis.delete(*keys)


memory_service = MemoryService()
