import pathlib
import struct
from typing import Final


# It's a class that defines a bunch of constants
class Config(struct.Struct):
    TEMP_FOLDER: Final = pathlib.Path(__file__).parent / "processing_temp"
    KUBO_PATH: Final = pathlib.Path(__file__).parent / "ipfs"
