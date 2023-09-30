import redis
from fastapi import APIRouter

quota_router = APIRouter(prefix="/data/quota")


from nuclei_backend.user_quota.quota_endpoints import *
from nuclei_backend.user_quota.quota_utils import *
