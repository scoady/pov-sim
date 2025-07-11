#!/bin/bash

# Configure Docker to allow insecure registry access

REGISTRY_URL="172.18.0.7:5000"

echo "Configuring Docker daemon for insecure registry access..."

# Create or update daemon.json
DAEMON_JSON="/etc/docker/daemon.json"
TEMP_JSON="/tmp/daemon.json"

if [ -f "$DAEMON_JSON" ]; then
    echo "Backing up existing daemon.json..."
    sudo cp "$DAEMON_JSON" "${DAEMON_JSON}.backup"
    
    # Add insecure-registries to existing config
    sudo jq ". + {\"insecure-registries\": [\"$REGISTRY_URL\"]}" "$DAEMON_JSON" > "$TEMP_JSON"
    sudo mv "$TEMP_JSON" "$DAEMON_JSON"
else
    echo "Creating new daemon.json..."
    echo "{\"insecure-registries\": [\"$REGISTRY_URL\"]}" | sudo tee "$DAEMON_JSON"
fi

echo "Restarting Docker daemon..."
sudo systemctl restart docker

echo "Waiting for Docker to restart..."
sleep 5

echo "Docker configured for insecure registry access to $REGISTRY_URL"
echo "You can now run: ./scripts/build-and-push.sh"