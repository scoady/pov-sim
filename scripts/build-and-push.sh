#!/bin/bash

# Script to build and load container images to kind cluster
# Usage: ./build-and-push.sh <appname>
# Example: ./build-and-push.sh flights

APP_NAME=$1
VALID_APPS=("airlines" "flights" "frontend" "proxy")

# Function to display usage
usage() {
    echo "Usage: $0 <appname>"
    echo "Valid app names: ${VALID_APPS[*]}"
    echo "Example: $0 flights"
    exit 1
}

# Check if app name is provided
if [ -z "$APP_NAME" ]; then
    echo "Error: App name is required"
    usage
fi

# Check if app name is valid
if [[ ! " ${VALID_APPS[*]} " =~ " ${APP_NAME} " ]]; then
    echo "Error: Invalid app name '$APP_NAME'"
    usage
fi

# Check if app directory exists
if [ ! -d "./$APP_NAME" ]; then
    echo "Error: Directory './$APP_NAME' does not exist"
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "./$APP_NAME/Dockerfile" ]; then
    echo "Error: Dockerfile not found in './$APP_NAME/'"
    exit 1
fi

echo "Building $APP_NAME image..."
docker build -t $APP_NAME:latest ./$APP_NAME

if [ $? -eq 0 ]; then
    echo "Loading $APP_NAME image to kind cluster..."
    kind load docker-image $APP_NAME:latest --name app-cluster
    
    if [ $? -eq 0 ]; then
        echo "$APP_NAME image built and loaded to kind cluster successfully!"
    else
        echo "Error: Failed to load $APP_NAME image to kind cluster"
        exit 1
    fi
else
    echo "Error: Failed to build $APP_NAME image"
    exit 1
fi
