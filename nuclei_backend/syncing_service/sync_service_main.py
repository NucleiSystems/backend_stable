import redis
from fastapi import APIRouter

sync_router = APIRouter(prefix="/data/sync")


from .sync_service_endpoints import *  # noqa: E402, F403
from .sync_util_endpoints import *
