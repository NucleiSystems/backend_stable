from __future__ import annotations

import logging
from typing import *  # noqa: F403

import sqlalchemy.exc
from fastapi import Depends, File, HTTPException, UploadFile

from nuclei_backend.users.user_models import User

from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from .ipfs_utils import *  # noqa: F403
from .main import storage_service


@storage_service.post("/upload")
async def upload(
    file_name: UploadFile = File(),
    db=Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("Uploading file")
    # get the file name
    file: bytes = file_name.file.read()
    try:
        cid: str = produce_cid(file, file_name)  # noqa: F405
        if not cid:
            raise HTTPException(status_code=400, detail="Failed to produce CID")
        _hash: str = generate_hash(cid)  # noqa: F405
        if not _hash:
            raise HTTPException(status_code=400, detail="Failed to generate hash")
        user: User = current_user
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    try:
        users_id = current_user.id
        data_record = assemble_record(  # noqa: F405
            file,
            file_name,
            cid,
            users_id,
        )

        db.add(data_record)
        db.commit()

    except sqlalchemy.exc.IntegrityError:
        return {"message": "File already exists", "file_hash": hash}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    return {
        "cid": cid,
        "hash": _hash,
        "user_id": current_user.username,
        "status": "success",
    }
