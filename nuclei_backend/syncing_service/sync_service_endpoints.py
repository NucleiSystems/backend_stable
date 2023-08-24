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
from .sync_user_cache import FileCacheEntry, FileListener, RedisController
from .sync_utils import (
    UserDataExtraction,
    get_collective_bytes,
    get_user_cid,
    get_user_cids,
)
import logging
import datetime


def process_file(user, db) -> None:
    try:
        cids = get_user_cids(user.id, db)
        get_collective_bytes(user.id, db)
        files = UserDataExtraction(user.id, db, cids)
        file_session_cache = FileCacheEntry(files.session_id)
        redis_controller = RedisController(user=str(user.id))
        files.download_file_ipfs()
        files.write_file_summary()
        if files.insurance():
            file_session_cache.activate_file_session()
        file_listener = FileListener(user.id, files.session_id)
        file_listener.file_listener()
        time.sleep(10)
        redis_controller.set_file_count(len(cids))

        try:
            files.cleanup()
        except Exception as e:
            print(e)

        file_session_cache.activate_file_session()

        redis_controller.close()
    except Exception as e:
        print(e)


def process_files(user, db):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        future = executor.submit(process_file, user, db)
        futures.append(future)

        results = [future.result() for future in futures]
    return results


@sync_router.get("/fetch/all")
async def dispatch_all(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        background_tasks.add_task(process_files, user, db)
        return {
            "message": "Dispatched",
        }, status.HTTP_202_ACCEPTED
    except Exception as e:
        return {"error": e}


# write a singular endpoint to point traffic
# to either the redis cache fetcher or to the file fetcher endpoint


@sync_router.on_event("startup")
@repeat_every(seconds=60 * 60 * 2)
async def clear_redis_schedular():
    try:
        user: User = get_current_user()
        logging.info(
            f"deleting {user.username}'s redis cache at: {str(datetime.datetime.now())}"
        )
        redis_instance = RedisController(user.id)
        redis_instance.clear_cache()
    except Exception as e:
        logging.error(
            f"there was an error in the clear_redis_schedular \
                saying {e} \
            at: {str(datetime.datetime.now())}"
        )


@sync_router.get("/fetch")
async def fetch_specific(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    item_ids: typing.List[int] = None,
):
    if item_ids is None:
        return {"message": "No item ids provided"}

    _redis = RedisController(str(user.id))
    all_files = _redis.get_files()
    _redis.close()
    all_files = json.loads(all_files)

    files_to_return = []

    for item_id in item_ids:
        files = UserDataExtraction(user.id, db, [get_user_cid(user.id, db, item_id)])
        files.download_file_ipfs()
        files.write_file_summary()

        # Validate checksum
        expected_checksum = None
        for name, file_data in all_files.items():
            if (
                file_data["file_name"] == files.file_name
            ):  # Adjust based on your data structure
                expected_checksum = file_data["checksum"]
                break

        if expected_checksum is None:
            print("Expected checksum not found for", files.file_name)
            continue

        calculated_checksum = hashlib.sha256(files.file_data).hexdigest()
        checksum_match = calculated_checksum == expected_checksum

        files.cleanup()

        file_listener = FileListener(user.id, files.session_id)
        file_listener.file_listener()

        file_index = (
            db.query(DataStorage)
            .filter(
                DataStorage.owner_id == user.id,
                DataStorage.file_name == files.file_name,
            )
            .first()
        )
        files_to_return.append(
            {
                "file_id": file_index.id,
                "checksum_match": checksum_match,
            }
        )

    return {"status": 200, "files": files_to_return}


@sync_router.get("/fetch/user_data")
def get_user_data_length(user: User = Depends(get_current_user), db=Depends(get_db)):
    return {
        "user_data_length": len(
            db.query(DataStorage).filter(DataStorage.owner_id == user.id).all()
        )
    }


@sync_router.get("/fetch/redis/all")
async def redis_cache_all(user: User = Depends(get_current_user)):
    try:
        _redis = RedisController(str(user.id))
        all_files = _redis.get_files()
        _redis.close()
        all_files = json.loads(all_files)

        return {"files": all_files}

    except Exception as e:
        print(e)


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


@sync_router.post("/fetch/delete/all")
def delete_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    db.query(DataStorage).delete()
    db.commit()
    return {"message": "deleted"}


@sync_router.get("/fetch/redis/clear")
async def redis_cache_clear(user: User = Depends(get_current_user)):
    return RedisController(str(user.id)).clear_cache()


@sync_router.get("/all")
def return_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    user_data = (
        db.query(User).filter(User.id == user.id).all(),
        db.query(DataStorage).filter(DataStorage.owner_id == user.id).all(),
    )

    return {
        "user": user_data,
    }
