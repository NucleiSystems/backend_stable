from __future__ import annotations

import datetime
import os
import pathlib
import subprocess
import time
from typing import LiteralString
from uuid import uuid4

from typing_extensions import LiteralString

from .config import Config
from .ipfs_model import DataStorage


def ensure_dir(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def save_temp_file(file, filename: str) -> str:
    unique_id = str(uuid4())
    temp_filename = f"{filename}-{unique_id}{filename[-4:]}"
    temp_file_path = pathlib.Path(Config.TEMP_FOLDER) / temp_filename

    with open(temp_file_path, "wb") as f:
        f.write(file)

    return str(temp_file_path)


def remove(path):
    os.remove(path)


def generate_hash(cid: LiteralString) -> str:
    unique_id = str(uuid4())
    hash_bat_path = pathlib.Path(Config.TEMP_FOLDER) / f"hash-{unique_id}.bat"
    buffer_path = pathlib.Path(Config.TEMP_FOLDER) / f"hash-{unique_id}.txt"

    with open(hash_bat_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(rf"cd {Config.TEMP_FOLDER}\n")
        f.write(rf"{Config.KUBO_PATH} ls -v {cid} > {buffer_path}")

    hash_bat_path.chmod(0o755)

    subprocess.run([hash_bat_path], shell=True)
    time.sleep(1)

    with open(buffer_path, "r") as f:
        _hash = f.read().strip()

    remove(hash_bat_path)
    remove(buffer_path)

    return _hash


def produce_cid(file: bytes, filename: str) -> LiteralString:
    ensure_dir(Config.TEMP_FOLDER)

    unique_id = str(uuid4())
    cid_bat_path = pathlib.Path(Config.TEMP_FOLDER) / f"cid-{unique_id}.sh"
    buffer_path = pathlib.Path(Config.TEMP_FOLDER) / f"cid-{unique_id}.txt"
    temp_file_path = save_temp_file(file, filename)

    with open(cid_bat_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(rf"cd {Config.TEMP_FOLDER}\n")
        f.write(
            rf"{Config.KUBO_PATH} add --quiet --pin {temp_file_path} > {buffer_path}\n"
        )

    cid_bat_path.chmod(0o755)
    subprocess.run([cid_bat_path], shell=True)
    time.sleep(1)

    with open(buffer_path, "r") as f:
        cid = f.read().strip()

    remove(cid_bat_path)
    remove(buffer_path)
    temp_file_path.unlink()

    return cid


def assemble_record(file: bytes, filename: str, cid: str, owner_id: int = None):
    return DataStorage(
        file_name=filename,
        file_cid=cid,
        file_hash=generate_hash(cid),
        file_size=len(file),
        file_type=os.path.splitext(file)[1],
        file_upload_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        owner_id=owner_id,
    )
