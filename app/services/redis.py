import json
import os
from typing import Any, Dict, Optional, Union
import redis.asyncio as aioredis
from pydantic import BaseModel
from app.core.config import settings

class RedisCacheService:
    def __init__(self):
        self.redis_url = settings.redis_url
        self.client: Optional[aioredis.Redis] = None

    def connect(self) -> aioredis.Redis:
        if not self.client:
            self.client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self.client

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None

    async def set_object(self, key: str, value: Union[Dict[str, Any], BaseModel], ex_seconds: Optional[int] = None) -> bool:
        """
        Serializes a dictionary or a Pydantic model instance into a JSON string 
        and stores it in Redis. Defaults to a 1-hour expiration.
        """
        if not self.client:
            self.connect()

        # Handle Pydantic models automatically
        if isinstance(value, BaseModel):
            serialized_value = value.model_dump_json()
        else:
            serialized_value = json.dumps(value)

        print(f"Setting key {key} in Redis with expiration {ex_seconds} seconds")
        return await self.client.set(name=key, value=serialized_value, ex=ex_seconds)

    async def get_object(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a JSON string from Redis and transforms it back into a Python dictionary.
        """
        if not self.client:
            self.connect()

        raw_data = await self.client.get(key)
        if not raw_data:
            print(f"No data found in Redis for key: {key}")
            return None

        try:
            print(f"Data retrieved from Redis for key {key}")
            return json.loads(raw_data)
        except (json.JSONDecodeError, TypeError):
            return None

    async def invalidate(self, key: str) -> bool:
        """
        Explicitly invalidates (deletes) a cache key when an underlying object changes.
        """
        if not self.client:
            self.connect()
        result = await self.client.delete(key)
        print(f"Token Invalidate successfuly: {result}")
        return result > 0

redis_cache = RedisCacheService()