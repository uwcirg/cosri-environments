#!/bin/sh -e

repo_path="$(cd "$(dirname "$0")" && pwd)"
cmdname="$(basename "$0")"

usage() {
    cat << USAGE >&2
Usage:
    $cmdname

    Docker deployment script
    Pull the latest docker image and recreate relevant containers

USAGE
    exit 1
}

if [ "$1" = -h ] || [ "$1" = --help ]; then
    usage
    exit 0
fi


# docker-compose commands must be run in the same directory as docker-compose.yaml
cd "${repo_path}"

echo "📦 Updating images..."
docker-compose pull

echo "🚀 Deploying containers..."
docker-compose up --detach
