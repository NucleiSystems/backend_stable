from fastapi import APIRouter

storage_service = APIRouter(prefix="/storage")

from .image_compression.image_compression_routes import *  # noqa: E402, F403
from .ipfs_routes import *  # noqa: E402, F403
from .misc_compression.misc_compression_routes import *  # noqa: E402, F403
