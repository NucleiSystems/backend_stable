import hashlib
import json
import time
import typing
import asyncio
from fastapi_utils.tasks import repeat_every
from fastapi import Depends
from fastapi import BackgroundTasks, status
from concurrent.futures import ThreadPoolExecutor

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_service_main import sync_router
from .sync_user_cache import (
    FileSessionManager,
    FileListener,
    RedisController,
    FileCleanerSchedule,
)
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
        file_session_cache = FileSessionManager(files.session_id)
        file_session_cache.activate_file_session()
        redis_controller = RedisController(user=str(user.id))
        files.download_file_ipfs()
        files.write_file_summary()

        file_listener = FileListener(user.id, files.session_id)
        file_listener.file_listener()
        time.sleep(10)
        redis_controller.set_file_count(len(cids))

        try:
            files.cleanup()
        except Exception as e:
            print(e)

        file_session_cache.deactivate_file_session()
        redis_controller.close()
        file_session_cache.close()
    except Exception as e:
        print(e)


async def process_files(user, db):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=8) as executor:
        future = loop.run_in_executor(executor, process_file, user, db)
        result = await future

    return result


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


@sync_router.on_event("startup")
@repeat_every(seconds=60 * 60 * 2)
async def clear_redis_schedular():
    print("scheduler started")
    try:
        session_manager = FileCleanerSchedule()
        session_manager.clean_expired_folders()

    except Exception as e:
        logging.error(
            f"there was an error in the clear_redis_schedular \
                saying {e} \
            at: {str(datetime.datetime.now())}"
        )


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


@sync_router.post("/fetch/delete/all")
def delete_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    db.query(DataStorage).delete()
    db.commit()
    return {"message": "deleted"}


@sync_router.get("/fetch/redis/clear")
async def redis_cache_clear(user: User = Depends(get_current_user)):
    return RedisController(str(user.id)).clear_cache()
