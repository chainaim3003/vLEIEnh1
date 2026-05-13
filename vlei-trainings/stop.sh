#!/bin/bash
echo "Stopping and removing training environment containers..."

# Stop and remove containers, networks defined in the docker-compose file
docker compose down

echo "Environment stopped."