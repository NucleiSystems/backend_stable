import socketio
from fastapi import FastAPI


class SocketManager:
    def __init__(self) -> None:
        self.server = socketio.AsyncServer(
            async_handlers=True,
            logger=True,
        )
        self.app = socketio.ASGIApp(self.server)

    @property
    def on(self):
        return self.server.on

    @property
    def send(self):
        return self.server.send

    def mount_to(self, path: str, app: FastAPI):
        app.mount(path, self.app)

    def send_files(self, sid, files):
        self.send(sid, files)
