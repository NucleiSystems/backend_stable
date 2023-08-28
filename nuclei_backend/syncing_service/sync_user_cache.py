import base64
import datetime
import hashlib
import json
import pathlib
import time
from os import environ
import redis


class RedisController:
    def __init__(self, user):
        self.redis_connection = redis.Redis().from_url(
            url="redis://127.0.0.1:6379", decode_responses=True, db=0
        )
        self.user = user

    def set_files(self, file: list[dict[str, bytes]]):
        return self.redis_connection.set(str(self.user), str(file))

    def get_files(self):
        return self.redis_connection.get(self.user)

    def clear_cache(self):
        return self.redis_connection.delete(self.user)

    def check_files(self):
        return self.redis_connection.exists(self.user)

    def set_file_count(self, count: int):
        return self.redis_connection.set(f"{self.user}_count", count)

    def get_file_count(self):
        return (
            int(self.redis_connection.get(f"{self.user}_count"))
            if self.redis_connection.exists(f"{self.user}_count")
            else 0
        )

    def delete_file_count(self):
        return self.redis_connection.delete(f"{self.user}_count")

    def close(self):
        return self.redis_connection.close()


class FileSessionManager:
    """A cache entry for a file in a directory."""

    def __init__(self, dir_id):
        """Create a new file cache entry for the specified directory."""
        self.dir_id = dir_id
        self.redis_connection = redis.Redis().from_url(
            url="redis://127.0.0.1:6379", decode_responses=True, db=1
        )
        self.time_delta = datetime.timedelta(seconds=30)
        self.time_now = time.time()

    def activate_file_session(self):
        """
        'processing:ebd69047-cd6d-4a10-a769-f5f810e4071e':169111333.1111111
        """
        self.redis_connection.set(
            f"processing:{self.dir_id}", self.time_delta.seconds + self.time_now
        )

    def deactivate_file_session(self):
        if self.redis_connection.exists(f"processing:{self.dir_id}"):
            self.redis_connection.delete(f"processing:{self.dir_id}")

    def close(self):
        return self.redis_connection.close()


class FileCleanerSchedule:
    def __init__(self) -> None:
        self.redis_connection = redis.Redis().from_url(
            url="redis://127.0.0.1:6379", decode_responses=True, db=1
        )
        self.all_sessions = [
            keys for keys in self.redis_connection.scan_iter("processing:*")
        ]

    def get_expired_sessions(self):
        "returns an array of expired keys"
        for sessions in self.all_sessions:
            if not self.is_expired(self.redis_connection.get(sessions)):
                self.all_sessions.remove(sessions)
        return self.all_sessions

    def is_expired(self, _time):
        "calculates the time_delta fed"
        if float(_time) < time.time():
            return True
        else:
            return False

    def clean_expired_folders(self):
        "checks and deletes expired folders, assumption is the folder is already expired"
        for sessions in self.get_expired_sessions():
            dir_name = str(sessions).split(":")[1]

            dir_path = (
                pathlib.Path(__file__).parent.absolute()
                / "FILE_PLAYING_FIELD"
                / dir_name
            )
            if dir_path.is_dir():
                dir_path.rmdir()
            self.redis_connection.delete(sessions)


class FileListener(RedisController):
    def __init__(self, user_id, session_id):
        super().__init__(user_id)
        self.user_id = user_id
        self.redis = RedisController(user_id)
        self.session_id = session_id

    def file_listener(self):
        """
        The `file_listener` function reads files from a directory,
        encodes them in base64, and stores them
        in a dictionary before saving the dictionary to a Redis database.
        """
        # self.path / str(self.session_id)
        time.sleep(2)
        files_index = open(f"{self.session_id}.internal.json", "r").read()
        data = json.loads(files_index)
        data = dict(data)
        data = data.items()
        dispatch_dict = {str(self.user_id): []}

        for _ in data:
            with open(_[0], "rb") as file_read_buffer:
                file_read_buffer = file_read_buffer.read()
            dispatch_dict[str(self.user_id)].append(
                {
                    str(_[0]): base64.encodebytes(file_read_buffer).decode(),
                    "data": {
                        "id": (str(_[1]["file_id"])),
                        "size": (str(_[1]["file_size"])),
                    },
                }
            )

        dispatch_dict = str(dispatch_dict).replace("'", '"')
        self.redis.set_files(dispatch_dict)
