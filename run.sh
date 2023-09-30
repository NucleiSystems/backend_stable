#!/bin/bash

# Pull the latest changes from the remote repository



# Activate the virtual environment
source venv/bin/activate

# Install or upgrade required packages
pip3 install --upgrade -r requirements.txt

# Generate a new Alembic revision


# Ensure execute permission for IPFS binary
chmod +x /home/backend_stable/nuclei_backend/storage_service/ipfs
chmod +x /home/backend_stable/nuclei_backend/syncing_service/utils/ipfs


# Start IPFS daemon and log output to ipfs.log
nohup /nuclei_backend/storage_service/ipfs daemon --init --enable-pubsub-experiment > ipfs.log 2>&1 &

# Start Uvicorn server
uvicorn nuclei_backend:app --host=0.0.0.0 --port=8000
