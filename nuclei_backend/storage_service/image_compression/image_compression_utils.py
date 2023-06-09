from concurrent.futures import ProcessPoolExecutor
import os
import pathlib
import psutil
import zstandard as zstd
import numpy as np

from ..CompressionBase import CompressionImpl


class CompressImage(CompressionImpl):
    def __init__(self, file: bytes, filename: str):
        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    def cleanup_compression_outcome(self):
        pathlib.Path(self.compression_temp_file[0]).unlink()

    def compress_data(self, data: bytes):
        try:
            cpu_percent = psutil.cpu_percent()
            mem_percent = psutil.virtual_memory().percent

            if cpu_percent >= 40 and mem_percent >= 40:
                file_size_mb = len(data) / 1024 / 1024

                level = 15 if self.compression_level == 1 and file_size_mb > 300 else 1
            elif mem_percent < 60:
                level = 20
            else:
                level = 22
            compressor = zstd.ZstdCompressor(level=level)
            return compressor.compress(data)
        except Exception as e:
            return e

    def produce_compression(self) -> bytes:
        with open(self.compression_temp_file[0], "rb") as f:
            original_data = np.fromfile(f, dtype=np.uint8)

        file_size = len(original_data)
        avg_image_size = 5000000  # example average size of an image in bytes
        if file_size < avg_image_size * 0.8:
            compression_processes = 1
            chunks = [original_data]
        else:
            compression_processes = os.cpu_count()
            (file_size // compression_processes) + 1
            chunks = np.array_split(original_data, compression_processes)

        with ProcessPoolExecutor(max_workers=compression_processes) as executor:
            compressed_chunks = executor.map(self.compress_data, chunks)

        return b"".join(list(compressed_chunks))
