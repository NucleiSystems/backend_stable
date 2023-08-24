#!/bin/bash
git pull

pip3 install -r requirements.txt
uuid=$(uuidgen)
alembic revision --autogenerate -m "$uuid"

chmod +x /home/backend_stable/nuclei_backend/storage_service/ipfs

# Start IPFS daemon and log output to ipfs.log
nohup /nuclei_backend/storage_service/ipfs daemon --init --enable-pubsub-experiment > ipfs.log 2>&1 &

# Start Uvicorn server
uvicorn nuclei_backend:app --host=0.0.0.0 --port=8000 #--workers=4