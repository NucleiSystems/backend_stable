import redis
from fastapi import APIRouter

sync_router = APIRouter(prefix="/data/sync")
redis_connection = redis.Redis(host="localhost", port=6379, db=0)


from .sync_service_endpoints import *  # noqa: E402, F403
