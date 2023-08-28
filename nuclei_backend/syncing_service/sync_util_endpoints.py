import hashlib
import json
import time
import typing
from fastapi_utils.tasks import repeat_every
from fastapi import Depends
from fastapi import BackgroundTasks, status
from concurrent.futures import ThreadPoolExecutor

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_service_main import sync_router
from .sync_user_cache import FileSessionManager, FileListener, RedisController
from .sync_utils import (
    UserDataExtraction,
    get_collective_bytes,
    get_user_cid,
    get_user_cids,
)


@sync_router.get("/fetch")
async def fetch_specific(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    item_ids: typing.List[int] = None,
):
    """
    Fetches specific files from the IPFS network
    """
    if item_ids is None:
        return {"message": "No item ids provided"}

    for item_id in item_ids:
        files = UserDataExtraction(user.id, db, [get_user_cid(user.id, db, item_id)])
        files.download_file_ipfs()
        files.write_file_summary()
        files.cleanup()

        file_listener = FileListener(user.id, files.session_id)
        file_listener.file_listener()

    _redis = RedisController(str(user.id))
    all_files = _redis.get_files()
    _redis.close()
    all_files = json.loads(all_files)
    files_to_return = []
    for name, _ in all_files:
        file_index = (
            db.query(DataStorage)
            .filter(DataStorage.owner_id == user.id, DataStorage.file_name == name)
            .first()
        )
        files_to_return.append(file_index.id)

    return {"status": 200, "files": files_to_return}


@sync_router.get("/fetch/user_data")
def get_user_data_length(user: User = Depends(get_current_user), db=Depends(get_db)):
    return {
        "user_data_length": len(
            db.query(DataStorage).filter(DataStorage.owner_id == user.id).all()
        )
    }


@sync_router.get("/delete/")
async def delete(
    image_index: int, user: User = Depends(get_current_user), db=Depends(get_db)
):
    db.query(DataStorage).filter(
        DataStorage.owner_id == user.id, DataStorage.id == image_index
    ).delete()

    _redis = RedisController(str(user.id))

    all_files = _redis.get_files()
    all_files = json.loads(all_files)

    all_files.pop(image_index)
    _redis.set_files(all_files)
    _redis.close()
    db.commit()

    return {"status": "deleted", "image_index": image_index}


@sync_router.get("/all")
def return_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    user_data = (
        db.query(User).filter(User.id == user.id).all(),
        db.query(DataStorage).filter(DataStorage.owner_id == user.id).all(),
    )

    return {
        "user": user_data,
    }
