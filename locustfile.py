import time
import urllib.parse
import uuid

from faker import Faker
from locust import HttpUser, TaskSet, task


class UserBehavior(TaskSet):
    token = None
    email = None
    username = None
    password = None
    uid = None

    @task(1)
    def register(self):
        fake = Faker()
        self.uid = uuid.uuid4()
        self.email = f"{fake.email()}{self.uid}"
        self.username = f"{fake.user_name()}{self.uid}"
        self.password = fake.password()

        payload = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
        }
        with self.client.post(
            "users/register", json=payload, catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure("Failed to register user")
        time.sleep(1)

    @task(2)
    def login(self):
        payload = {
            "grant_type": "",
            "username": self.username,
            "password": self.password,
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        encoded_payload = urllib.parse.urlencode(payload)
        with self.client.post(
            "users/token", headers=headers, data=encoded_payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                response.success()
            else:
                response.failure("Failed to login user")
        time.sleep(1)

    @task(3)
    def compress_image(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        files = {"files": ("250.png", open("250.png", "rb"), "image/png")}
        with self.client.post(
            "storage/compress/image?ipfs_flag=true",
            headers=headers,
            files=files,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Failed to compress image. Status code: {response.status_code}"
                )
        time.sleep(1)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    min_wait = 5000
    max_wait = 15000
