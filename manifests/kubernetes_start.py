import pathlib
import subprocess  # noqa: E401

manifest_files = [
    pathlib.Path("postgres-development.yaml"),
    pathlib.Path("redis-server-development.yaml"),
    pathlib.Path("ipfs-development.yaml"),
    pathlib.Path("PersistantVolume.yaml"),
    pathlib.Path("PersistentVolumeClaim.yaml"),
    pathlib.Path("nuclei-backend-development.yaml"),
]

for manifest in manifest_files:
    apply_command = f"kubectl apply -f {manifest}"
    subprocess.run(apply_command.split())
