from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from functools import lru_cache
import uuid
import secrets


class Nuclei(FastAPI):
    def __init__(
        self,
        *,
        title: str = "Nuclei",
        description: str = "Nuclei API",
        version: str = "0.1.0",
    ):
        super().__init__(title=title, description=description, version=version)
        self.add_models()
        self.configure_middleware()
        self.add_routes()

    @lru_cache(maxsize=None)
    def configure_middleware(self):
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.add_middleware(
            SessionMiddleware,
            secret_key=f"{uuid.uuid4()}{secrets.token_hex(25)}{uuid.uuid4()}{secrets.token_urlsafe(25)}",
        )

    @lru_cache(maxsize=None)
    def add_routes(self):
        from nuclei_backend.users.main import users_router
        from nuclei_backend.storage_service.main import storage_service
        from nuclei_backend.syncing_service.sync_service_main import sync_router

        self.include_router(storage_service)
        self.include_router(users_router)
        self.include_router(sync_router)

    @lru_cache(maxsize=None)
    def add_models(self):
        from .database import engine

        from .storage_service import ipfs_model
        from .users import user_models

        user_models.Base.metadata.create_all(bind=engine)
        ipfs_model.Base.metadata.create_all(bind=engine)


app = Nuclei()
