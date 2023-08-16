#!/bin/bash

# Define your VPS SSH details
VPS_USER="root"
VPS_HOST="170.64.180.130"
VPS_SSH_KEY_PATH="./id_rsa"

# Define the service you want to restart
SERVICE_NAME="nuclei_backend.service"

# SSH into the VPS and restart the service
ssh -o StrictHostKeyChecking=no -i "$VPS_SSH_KEY_PATH" "$VPS_USER@$VPS_HOST" "sudo systemctl restart $SERVICE_NAME"
