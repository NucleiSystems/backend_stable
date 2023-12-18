import contextlib
import json
import logging
import os
import pathlib
import shutil
import subprocess
import time
from uuid import uuid4
from fastapi import HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ..storage_service.ipfs_model import DataStorage


def get_user_cids(user_id, db) -> list:
    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return query
    except Exception as e:
        logging.error(f"An Error occurred in get_user_cids: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_user_cid(user_id, db, item_id) -> list:
    try:
        query = (
            db.query(DataStorage)
            .filter(DataStorage.owner_id == user_id, DataStorage.id == item_id)
            .first()
        )
        return query
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_collective_bytes(user_id, db):
    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return sum(x.file_size for x in query)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


class UserDataExtraction:
    def __init__(self, user_id, db, cids: list):
        self.user_id = user_id
        self.session_id = uuid4()
        self.db = db
        self.user_data = get_user_cids(self.user_id, self.db)
        self.file_bytes = []
        self.cids = cids

        self.new_folder = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), f"FILE_PLAYING_FIELD/{self.session_id}"
            )
        )
        self.ipfs_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "utils/ipfs")
        )

    async def download_file(self, cid):
        try:
            subprocess.check_call(
                [
                    f"{self.ipfs_path}",
                    "get",
                    cid.file_cid,
                    "-o",
                    cid.file_name,
                    "--progress=true",
                ]
            )
        except Exception as e:
            raise e

    async def download_files_async(self):
        with ThreadPoolExecutor(max_workers=len(self.cids)) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, self.download_file, cid)
                for cid in self.cids
            ]
            await asyncio.gather(*tasks)

    def download_file_ipfs(self):
        os.mkdir(self.new_folder)
        os.chdir(self.new_folder)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_files_async())

        self.write_file_summary()

        while not self.insurance():
            time.sleep(5)

    def write_file_summary(self):
        with contextlib.suppress(PermissionError):
            file_sum = {
                cid.file_name: {
                    "file_name": cid.file_name,
                    "file_cid": cid.file_cid,
                    "file_size": cid.file_size,
                    "file_id": cid.id,
                }
                for cid in self.cids
            }
            with open(f"{self.session_id}.internal.json", "w") as f:
                json.dump(file_sum, f)

    def insurance(self) -> bool:
        for cid in self.cids:
            if not os.path.isfile(f"{cid.file_name}"):
                return False
            _bytes = open(cid.file_name, "rb")
            if len(_bytes.read()) != cid.file_size:
                return False
            del _bytes
        return True

    def cleanup(self):
        with contextlib.suppress(PermissionError):
            os.chdir(pathlib.Path(self.new_folder).parent)

            shutil.rmtree(
                pathlib.Path(self.new_folder),
                ignore_errors=False,
            )
