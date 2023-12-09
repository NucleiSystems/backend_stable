from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import BackgroundTasks, Depends, HTTPException, UploadFile, status

from ...users.auth_utils import get_current_user
from ...users.user_handler_utils import get_db
from ..main import storage_service
from .image_compression_utils import CompressImage
import logging


def process_file(
    file: bytes, filename: str, ipfs_flag: bool, identity_token: str, db
) -> None:
    try:
        compressing_file = CompressImage(file, filename)

        print("files compressed")
        compressed_file = compressing_file.produce_compression()
        if ipfs_flag:
            print("before ipfs flag")
            try:
                with db as _db:
                    compressing_file.commit_to_ipfs(
                        compressed_file, filename, identity_token, _db
                    )
            except Exception as e:
                print(f"the error was {e}")
        compressing_file.cleanup_compression_outcome()
    except Exception as e:
        print(f"Error compressing and storing file {filename}: {str(e)}")


def process_files(
    files: List[UploadFile],
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    for file in files:
        _filename = file.filename.replace(" ", "_")
        _file = file.file.read()
        process_file(_file, _filename, ipfs_flag, identity_token, db)


@storage_service.post("/compress/image")
async def compress_task_image(
    files: List[UploadFile],  # noqa: F405
    background_tasks: BackgroundTasks,
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded",
        )
    try:
        logging.debug("sending the task to background")
        background_tasks.add_task(process_files, files, ipfs_flag, identity_token, db)

        return {
            "message": "Files submitted for compression",
            "files": [file.filename for file in files],
        }, status.HTTP_202_ACCEPTED
    except Exception as e:
        return {"error": e}
