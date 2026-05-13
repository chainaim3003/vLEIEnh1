#!/bin/bash

# Check if vlei network exists, create it if not
# echo "Checking for keri_network..."
# if ! docker network ls | grep -q keri_network; then
#     echo "keri_network not found. Creating it..."
#     docker network create keri_network
# else
#     echo "keri_network already exists."
# fi

# Stop and remove existing containers, networks defined in the compose file
echo "Stopping and removing existing containers..."
docker compose down

# Build images (if Dockerfiles changed) and start services in detached mode
echo "Building images and starting containers..."
docker compose up --build -d --scale direct-sally=0

echo "Deployment complete!"
echo "Access JupyterLab at: http://localhost:8888"