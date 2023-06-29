#!/bin/bash

# Start IPFS daemon and log output to ipfs.log
nohup /nuclei_backend/storage_service/ipfs daemon --init --enable-pubsub-experiment > ipfs.log 2>&1 &

# Start Uvicorn server
uvicorn nuclei_backend:app --host=0.0.0.0 --port=8000 --workers=4
