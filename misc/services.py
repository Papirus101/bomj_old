import aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

redis = aioredis.from_url("redis://127.0.0.1:6379", decode_responses=True)
scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))