import logging
import pathlib
import psutil
from concurrent.futures import ProcessPoolExecutor
import os
import numpy as np
import zstandard as zstd

from ..CompressionBase import CompressionImpl

logger = logging.getLogger(__name__)


class CompressImage(CompressionImpl):
    def __init__(self, file: bytes, filename: str):
        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    def cleanup_compression_outcome(self):
        pathlib.Path(self.compression_temp_file[0]).unlink()

    def produce_compression(self) -> bytes:
        print("compressing image")
        with open(self.compression_temp_file[0], "rb") as f:
            original_data = f.read()

        try:
            compressor = zstd.ZstdCompressor(level=15)
            return compressor.compress(original_data)
        except Exception as e:
            print(f"Error compressing image: {str(e)}")
            return b""
