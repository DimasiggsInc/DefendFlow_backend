from cashews import cache
from src.config import settings

cache.setup(settings.REDIS_URL)

