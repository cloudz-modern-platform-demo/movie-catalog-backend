#!/bin/zsh
set -e

# Load shell configuration to get aliases
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

APP_NAME=movie-catalog-backend
APP_VERSION=0.2.0

docker build --platform linux/amd64 -t localhost/${APP_NAME}:${APP_VERSION} --tls-verify=false -f ./Dockerfile
docker tag localhost/${APP_NAME}:${APP_VERSION} zcr.cloudzcp.net/cloudzcp/${APP_NAME}:${APP_VERSION}
docker push zcr.cloudzcp.net/cloudzcp/${APP_NAME}:${APP_VERSION} --tls-verify=false
