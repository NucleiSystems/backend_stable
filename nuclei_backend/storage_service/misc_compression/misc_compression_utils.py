import logging
import pathlib
import subprocess
import time
from typing import Final
from uuid import uuid4

import lz4.frame
from fastapi import File
from lz4.block import compress, decompress

from ..CompressionBase import CompressionImpl
from ..ipfs_utils import *

logger = logging.getLogger(__name__)


class CompressMisc(CompressionImpl):
    """Compress video with ffmpeg"""

    def __init__(self, file: bytes, filename):
        super().__init__(app_path="misc")
        self.file = file
        self.filename = filename
        self.temp_dir = self.save_to_temp(file, filename)

        self.dir_to_cleanup = {
            "compression": f'{str(self.temp_dir[0])[:str(self.temp_dir[0]).index(r"_compression_temp")]}_compression_temp',  # noqa: E501
            "processing": pathlib.Path(
                f'{str(self.temp_dir[0])[:str(self.temp_dir[0]).index(r"_compression_temp")]}processing_temp'
            ).parent.parent.joinpath("processing_temp"),
        }

    def cleanup_compression_outcome(self):
        self.cleanup_file(rf"{self.dir_to_cleanup['compression']}\{self.temp_dir[1]}")
        self.cleanup_file(self._file_name)

    def produce_compression(self) -> bytes:
        """Produce the compression"""
        result = lz4.frame.compress(
            self.file,
            compression_level=lz4.frame.COMPRESSIONLEVEL_MAX,
            block_size=lz4.frame.BLOCKSIZE_MAX1MB,
            block_linked=True,
            content_checksum=True,
        )
        self._file_name = f"{self.dir_to_cleanup['compression']}\{self.filename[:self.filename.index('.')]}.lz4"  # noqa: E501, E999

        print("file name ", self._file_name)
        with open(self._file_name, "wb") as fout:
            fout.write(result)

        return open(pathlib.Path(self._file_name), "rb", buffering=0).read()
