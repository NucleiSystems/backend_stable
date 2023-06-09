from fastapi import APIRouter

users_router = APIRouter(prefix="/users")

from .auth_routes import *  # noqa: E402, F403
from .user_handler import *  # noqa: E402, F403
