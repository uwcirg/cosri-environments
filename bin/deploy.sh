#!/bin/sh -e
cmdname="$(basename "$0")"
bin_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="$(readlink -f ${bin_path}/..)"

usage() {
    cat << USAGE >&2
Usage:
    $cmdname [--help|-h]


    Meta-deployment script; call deployment scripts for each Cosri component

USAGE
    exit 1
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

get_compose_project() {
    # get path to first active docker-compose project, given project name
    local repo_path="$1"
    local compose_project_dir_name="$2"
    # assume project is in use based on presence of .env file
    echo "$(dirname $(find "$repo_path" -path "*/$compose_project_dir_name/.env" -print -quit))"
}

COMPONENTS='femr logs cosri'
for component in $COMPONENTS; do
    project_path="$(get_compose_project $repo_path $component)"

    if [ -z $project_path ]; then
        continue
    fi

    echo Deploying $component in $project_path...
    ${project_path}/deploy*.sh
done
