import asyncio
import logging
import pathlib
import zlib

from aiofiles import open as aio_open
from concurrent.futures import ProcessPoolExecutor

from ..CompressionBase import CompressionImpl

logger = logging.getLogger(__name__)


class CompressImage(CompressionImpl):
    def __init__(self, file: bytes, filename: str):
        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    async def cleanup_compression_outcome(self):
        try:
            await asyncio.to_thread(pathlib.Path(self.compression_temp_file[0]).unlink)
        except FileNotFoundError:
            pass

    def compress_chunk(self, chunk):
        return zlib.compress(chunk)

    async def produce_compression(self) -> bytes:
        print("compressing image")
        async with aio_open(self.compression_temp_file[0], "rb") as f:
            original_data = await f.read()

        chunk_size = 8192  # Adjust the chunk size based on your requirements
        chunks = [
            original_data[i : i + chunk_size]
            for i in range(0, len(original_data), chunk_size)
        ]

        with ProcessPoolExecutor() as executor:
            compressed_chunks = await asyncio.to_thread(
                executor.map, self.compress_chunk, chunks
            )

        return b"".join(compressed_chunks)
