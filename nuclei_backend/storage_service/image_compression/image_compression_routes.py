from concurrent.futures import ThreadPoolExecutor

from fastapi import BackgroundTasks, Depends, HTTPException, UploadFile, status

from ...users.auth_utils import get_current_user
from ...users.user_handler_utils import get_db
from ..ipfs_utils import *
from ..main import storage_service
from .image_compression_utils import CompressImage
from typing import List
import io


# def process_file(
#     file: bytes, filename: str, ipfs_flag: bool, identity_token: str, db
# ) -> None:
#     try:
#         compressing_file = CompressImage(file, filename)

#         print("files compressed")
#         compressed_file = compressing_file.produce_compression()
#         print(compressed_file)
#         if ipfs_flag:
#             print("before ipfs flag")
#             try:
#                 compressing_file.commit_to_ipfs(
#                     compressed_file, filename, identity_token, db
#                 )
#             except Exception as e:
#                 print(f"the error was {e}")
#         compressing_file.cleanup_compression_outcome()
#     except Exception as e:
#         print(f"Error compressing and storing file {filename}: {str(e)}")


# def process_files(
#     files: List[UploadFile],
#     ipfs_flag: bool | None = True,
#     identity_token: str = Depends(get_current_user),
#     db=Depends(get_db),
# ):
#     with ThreadPoolExecutor(max_workers=8) as executor:
#         futures = []
#         for file in files:
#             _filename = file.filename.replace(" ", "_")
#             _file = file.file.read()  # Read the file contents as bytes
#             future = executor.submit(
#                 process_file, _file, _filename, ipfs_flag, identity_token, db
#             )
#             futures.append(future)

#         results = [future.result() for future in futures]
#     return results


# @storage_service.post("/compress/image")
# async def compress_task_image(
#     files: List[UploadFile],  # noqa: F405
#     background_tasks: BackgroundTasks,
#     ipfs_flag: bool | None = True,
#     identity_token: str = Depends(get_current_user),
#     db=Depends(get_db),
# ):
#     # print the files
#     for file in files:
#         print(file.filename)
#         print(file.file)

#     if not files:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No file uploaded",
#         )
#     try:
#         background_tasks.add_task(process_files, files, ipfs_flag, identity_token, db)

#         return {
#             "message": "Files submitted for compression",
#             "files": [file.filename for file in files],
#         }, status.HTTP_202_ACCEPTED
#     except Exception as e:
#         return {"error": e}


@storage_service.post("/compress/image")
async def compress_task_image(
    files: List[UploadFile],
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    for file in files:
        _file = file.file
        _file = _file.read()
        _filename = file.filename.replace(" ", "_")

        if identity_token is None:
            return {"message": "Unauthorized user"}, status.HTTP_401_UNAUTHORIZED
        if not file:
            return {"error": "No file uploaded"}

        compressing_file = CompressImage(_file, _filename)

        compressed_file = compressing_file.produce_compression()
        if ipfs_flag:
            compressing_file.commit_to_ipfs(
                compressed_file, _filename, identity_token, db
            )
        compressing_file.cleanup_compression_outcome()
    return {"message": "Successfully compressed video"}, status.HTTP_200_OK
