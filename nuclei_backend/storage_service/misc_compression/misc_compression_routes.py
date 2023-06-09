
from fastapi import Depends, UploadFile, status

from nuclei_backend.users.auth_utils import get_current_user

from ...users.user_handler_utils import get_db
from ..ipfs_utils import *  # noqa: F403
from ..main import storage_service
from .misc_compression_utils import CompressMisc

# https://stackoverflow.com/questions/70043665/fastapi-unvicorn-request-hanging-during-invocation-of-call-next-path-operation


@storage_service.post("/compress/files")
def compress_task_misc(
    files: List[UploadFile],  # noqa: F405
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):

    for file in files:
        _file = file.file
        _file = _file.read()
        _filename = file.filename

        if identity_token is None:
            return {"message": "Unauthorised user"}, status.HTTP_401_UNAUTHORIZED
        if not file:
            return {"error": "No file uploaded"}

        compressing_file = CompressMisc(_file, _filename)

        compressed_file = compressing_file.produce_compression()
        if ipfs_flag:
            compressing_file.commit_to_ipfs(
                compressed_file, _filename, identity_token, db
            )
        compressing_file.cleanup_compression_outcome()
    return {"message": "Successfully compressed file"}, status.HTTP_200_OK
