import logging
import pathlib
import psutil
import zlib

from ..CompressionBase import CompressionImpl

logger = logging.getLogger(__name__)


class CompressImage(CompressionImpl):
    def __init__(self, file: bytes, filename: str):
        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    def cleanup_compression_outcome(self):
        try:
            pathlib.Path(self.compression_temp_file[0]).unlink()
        except FileNotFoundError:
            pass

    def produce_compression(self) -> bytes:
        print("Compressing image")
        chunk_size = 8192  # Adjust the chunk size based on your requirements

        with open(self.compression_temp_file[0], "rb") as f:
            with zlib.compressobj() as compressor:
                compressed_data = b""
                while chunk := f.read(chunk_size):
                    compressed_data += compressor.compress(chunk)

                # Flush the compressor
                compressed_data += compressor.flush()

        return compressed_data
