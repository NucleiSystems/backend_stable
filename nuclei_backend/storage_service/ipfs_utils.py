from __future__ import annotations

import datetime
import os
import os.path
import pathlib
import time
from typing import *  # noqa: F403
from uuid import uuid4

from typing_extensions import LiteralString

from .config import Config
from .ipfs_model import DataStorage


def ensure_dir(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def save_temp_file(file, filename: str) -> str:
    unique_id = str(uuid4())
    _filename = f"filename{unique_id}.{filename[-4:]}"
    _file_path = os.path.join(Config.TEMP_FOLDER, _filename)

    with open(_file_path, "wb") as f:
        f.write(file)

    return _file_path


def remove(path):
    os.remove(path)


def generate_hash(cid: LiteralString) -> str:
    unique_id = str(uuid4())
    _bat_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.bat")
    _buffer_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.txt")

    with open(_bat_path, "w") as f:
        f.write("#!/bin/bash")
        f.write("\n")
        f.write(rf"cd {Config.TEMP_FOLDER}")
        f.write("\n")
        f.write(rf"{Config.KUBO_PATH} ls -v {cid} > hash{unique_id}.txt")

    os.chmod(_bat_path, 0b111101101)

    os.popen(_bat_path)
    time.sleep(1)

    with open(_buffer_path, "r") as f:
        _hash = f.read().strip()

    remove(_bat_path)
    remove(_buffer_path)

    return _hash


def produce_cid(file: bytes, filename: str) -> LiteralString:
    if not os.path.exists(Config.TEMP_FOLDER):
        ensure_dir(Config.TEMP_FOLDER)
    try:
        path = str(Config.TEMP_FOLDER)
        unique_id = str(uuid4())
        _bat_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.sh")
        _buffer_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.txt")
        _temp_file_path = save_temp_file(file, filename)
    except Exception as e:
        raise e
    print(_temp_file_path)

    with open(_bat_path, "w") as f:
        f.write("#!/bin/bash")
        f.write("\n")
        f.write(rf"cd {Config.TEMP_FOLDER}")
        f.write("\n")
        f.write(
            rf"{Config.KUBO_PATH} add --quiet --pin {_temp_file_path} > {path}/cid{unique_id}.txt"  # noqa: E501
        )

    os.chmod(_bat_path, 0b111101101)
    os.popen(_bat_path)
    time.sleep(1)
    with open(pathlib.Path(_buffer_path), "r") as f:
        cid = f.read().strip()

    remove(_bat_path)
    remove(_buffer_path)
    pathlib.Path(_temp_file_path).unlink()

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
