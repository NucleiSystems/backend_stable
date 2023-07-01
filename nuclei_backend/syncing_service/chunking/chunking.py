import hashlib
import os
import uuid

# import the queue class from Python Standard Library


class Chunker:
    def __init__(self, file_name, size) -> None:
        self.file_name = file_name
        self.size = size
        self.primary_uuid = uuid.uuid4()
        self.original_file_hash = ""
        self.chunk_file_hashes = []
        self.chunk_file_uid = []
        self.chunk_amounts = 0

    def chunks(self):
        """
        It reads the file in chunks of size `_size` and yields the content of each chunk
        """
        _size = os.stat(self.file_name).st_size // self.size
        with open(self.file_name, "rb") as f:
            while content := f.read(_size):
                yield content

    def produce_chunks(self):
        """
        It takes a file, splits it into chunks, and writes each chunk to a file
        """
        split_files = self.chunks()
        count = 0
        for chunk in split_files:
            _hash = hashlib.sha256()
            _file_chunk_uid = uuid.uuid4()
            with open(
                f"{self.primary_uuid}_chunk_{_file_chunk_uid}_{count}.chunk", "wb+"
            ) as f:
                _hash.update(f.read())
                count += 1
                f.write(bytes(chunk))
            self.chunk_file_uid.append(_file_chunk_uid)
            self.chunk_file_hashes.append(_hash.hexdigest())

    def hasher(self):
        """
        It takes a file and hashes it.
        """
        _hash = hashlib.sha256()
        with open(self.file_name, "rb") as file:
            chunk = 0
            while chunk != b"":
                chunk = file.read(1024)
                _hash.update(chunk)

        self.original_file_hash = _hash.hexdigest()

    def write_ccif(self):
        """
        It writes the file's information to a file with the same name as the file's primary UUID.
        """  # noqa: E501
        with open(f"{self.primary_uuid}.ccif", "wb+") as ccif:
            ccif.write(bytes(str(self.primary_uuid), "utf-8"))
            ccif.write(bytes("\n", "utf-8"))

            ccif.write(bytes(str(self.file_name), "utf-8"))
            ccif.write(bytes("\n", "utf-8"))

            ccif.write(bytes(str(self.size), "utf-8"))
            ccif.write(bytes("\n", "utf-8"))

            ccif.write(bytes(str(self.original_file_hash), "utf-8"))
            ccif.write(bytes("\n", "utf-8"))

            ccif.write(bytes(str(self.chunk_file_hashes), "utf-8"))
            ccif.write(bytes("\n", "utf-8"))

            ccif.write(bytes(str(self.chunk_file_uid), "utf-8"))

    def generic_run(self):
        self.produce_chunks()
        self.hasher()
        self.write_ccif()


class Reconstruct:
    def __init__(self, ccif_file) -> None:
        self.ccif_file = ccif_file
        self.file_name = ""
        self.size = 0
        self.original_file_hash = ""
        self.chunk_file_hashes = []
        self.chunk_file_uid = []
        self.primary_uuid = ""

    def parser(self, data):
        """
        It takes a string of the form `"[UUID(a), UUID(b), UUID(c)]"` and returns a list of the form
        `["a", "b", "c"]`

        :param data: The data to be parsed
        :return: A list of strings.
        """  # noqa: E501
        return [
            elem.strip("' ")
            for elem in data.strip("[]\n")
            .replace("UUID(", "")
            .replace(")", "")
            .split(",")
        ]

    def parse_ccif_file(self):
        """
        It reads a file and then parses the data into a list
        """
        with open(self.ccif_file, "rb") as ccif:
            self.primary_uuid: str = ccif.readline().decode("utf-8")

            self.file_name: str = ccif.readline().decode("utf-8")
            self.size: int = ccif.readline().decode("utf-8")
            self.original_file_hash: str = ccif.readline().decode("utf-8")
            self.chunk_file_hashes: list = ccif.readline().decode("utf-8")
            self.chunk_file_uid: list = ccif.readline().decode("utf-8")

        self.primary_uuid = self.parser(self.primary_uuid)

        self.chunk_file_uid = self.parser(self.chunk_file_uid)
        self.chunk_file_hashes = self.parser(self.chunk_file_hashes)
        self.file_name = self.file_name.strip("\n")
        self.size = str(self.size).strip("\n")
        self.original_file_hash = self.original_file_hash.strip("\n")

    def chunk_files(self) -> list:
        """
        It returns a list of files in the current directory that contain the string "_chunk_" and the
        first character of the primary_uuid attribute of the object
        :return: A list of files that are sorted by the chunk number.
        """  # noqa: E501

        return sorted(
            [
                file
                for file in os.listdir()
                if "_chunk_" in file and self.primary_uuid[0] in file
            ],
            key=lambda file: int(file.split("_")[-1].split(".")[0]),
        )

    def construct_file(self):
        """
        It opens the file that we want to reconstruct, then iterates through the chunk files and writes
        them to the reconstructed file
        """  # noqa: E501
        with open(f"reconstructed/{self.file_name}", "wb+") as reconstructed_file:
            for chunk in self.chunk_files():
                with open(chunk, "rb") as chunk_file:
                    reconstructed_file.write(chunk_file.read())

    def ensure_integrity(self):
        """
        It reads the file in chunks of 1024 bytes and updates the hash object with each chunk
        :return: The return value is a boolean value.
        """  # noqa: E501
        _hash = hashlib.sha256()
        with open(f"reconstructed/{self.file_name}", "rb") as file:
            chunk = 0
            while chunk != b"":
                chunk = file.read(1024)
                _hash.update(chunk)

        if _hash.hexdigest() == self.original_file_hash:
            return True
        else:
            return False

    def run(self):
        """
        The function runs the parse_ccif_file() function, then the construct_file() function, then the
        ensure_integrity() function
        """  # noqa: E501
        self.parse_ccif_file()
        self.construct_file()
        if self.ensure_integrity():
            print("File integrity ensured")


def scan_for_ccif_files():
    """
    It returns a generator object that yields the name of each file in the current directory that ends
    with ".ccif"
    """  # noqa: E501
    for file in os.listdir():
        if file.endswith(".ccif"):
            yield file
