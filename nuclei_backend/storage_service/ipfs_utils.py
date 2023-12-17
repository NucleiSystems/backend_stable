from __future__ import annotations

import asyncio
import datetime
import os
import pathlib
import time
import zlib
from typing import Literal
from uuid import uuid4

from aiofiles import open as aio_open
from typing_extensions import LiteralString

from .config import Config
from .ipfs_model import DataStorage


async def ensure_dir(path: str) -> None:
    await asyncio.to_thread(pathlib.Path(path).mkdir, parents=True, exist_ok=True)


async def save_temp_file(file, filename: str) -> str:
    unique_id = str(uuid4())
    _filename = f"filename{unique_id}.{filename[-4:]}"
    _file_path = os.path.join(Config.TEMP_FOLDER, _filename)

    async with aio_open(_file_path, "wb") as f:
        await f.write(file)

    return _file_path


async def remove(path):
    await asyncio.to_thread(os.remove, path)


async def generate_hash(cid: LiteralString) -> str:
    unique_id = str(uuid4())
    _bat_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.bat")
    _buffer_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.txt")

    async with aio_open(_bat_path, "w") as f:
        await f.write("#!/bin/bash")
        await f.write("\n")
        await f.write(rf"cd {Config.TEMP_FOLDER}")
        await f.write("\n")
        await f.write(rf"{Config.KUBO_PATH} ls -v {cid} > hash{unique_id}.txt")

    os.chmod(_bat_path, 0b111101101)

    os.popen(_bat_path)
    time.sleep(1)

    async with aio_open(_buffer_path, "r") as f:
        _hash = await f.read()

    await remove(_bat_path)
    await remove(_buffer_path)

    return _hash


async def produce_cid(file: bytes, filename: str) -> LiteralString:
    await ensure_dir(Config.TEMP_FOLDER)
    try:
        path = str(Config.TEMP_FOLDER)
        unique_id = str(uuid4())
        _bat_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.sh")
        _buffer_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.txt")
        _temp_file_path = await save_temp_file(file, filename)
    except Exception as e:
        raise e
    print(_temp_file_path)

    async with aio_open(_bat_path, "w") as f:
        await f.write("#!/bin/bash")
        await f.write("\n")
        await f.write(rf"cd {Config.TEMP_FOLDER}")
        await f.write("\n")
        await f.write(
            rf"{Config.KUBO_PATH} add --quiet --pin {_temp_file_path} > {path}/cid{unique_id}.txt"  # noqa: E501
        )

    os.chmod(_bat_path, 0b111101101)
    os.popen(_bat_path)
    time.sleep(1)
    async with aio_open(pathlib.Path(_buffer_path), "r") as f:
        cid = await f.read()

    await remove(_bat_path)
    await remove(_buffer_path)
    pathlib.Path(_temp_file_path).unlink()

    return cid


async def assemble_record(file: bytes, filename: str, cid: str, owner_id: int = None):
    return DataStorage(
        file_name=filename,
        file_cid=cid,
        file_hash=await generate_hash(cid),
        file_size=len(file),
        file_type=os.path.splitext(file)[1],
        file_upload_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        owner_id=owner_id,
    )
