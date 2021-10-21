#!/bin/sh -e

cmdname="$(basename "$0")"
bin_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="${bin_path}/.."


usage() {
    cat << USAGE >&2
Usage:
    $cmdname [-h] [-b backup_location] compose_project_dir [compose_project_services...]
    -h     Show this help message
    -b     Override default backup location (/tmp)

    Application backup script
    Dump application database and uploaded content

USAGE
    exit 1
}

while getopts "hb:" option; do
    case "${option}" in
        b)
            backups_dir="${OPTARG}"
            ;;
        h)
            usage
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

default_backups_dir=/tmp
BACKUPS_DIR="${backups_dir:-$default_backups_dir}"

COMPOSE_PROJECT_DIR="$1"
# remove arg from argv
shift

# remaining args are docker-compose services
COMPOSE_PROJECT_SERVICES=$@

# if none given, back up all
if [ -z "$COMPOSE_PROJECT_SERVICES" ]; then
    COMPOSE_PROJECT_SERVICES="keycloak fhir"
fi


get_compose_project() {
    # get path to first active docker-compose project, given project name
    local repo_path="$1"
    local compose_project_dir_name="$2"
    # assume project is in use based on presence of .env file
    echo "$(dirname $(find "$repo_path" -path "*/$compose_project_dir_name/.env" -print -quit))"
}

dump_db() {
    # get path to first active docker-compose project, given project name
    local db_name="$1"
    local dump_filename="$2"

    echo Backing up $db_name...
    docker-compose exec -T --user postgres db bash -c "\
        pg_dump \
            --dbname $db_name \
            --no-acl \
            --no-owner \
            --encoding utf8 "\
    > "${BACKUPS_DIR}/${dump_filename}-${db_name}.sql"
    echo "Backup written to ${BACKUPS_DIR}/${dump_filename}-${db_name}.sql"
}


docker_compose_directory="$(get_compose_project "$repo_path" "$COMPOSE_PROJECT_DIR")"

# docker-compose commands must be run in the same directory as docker-compose.yaml
cd "${docker_compose_directory}"

if [ -z "$(docker-compose ps --quiet db)" ]; then
    >&2 echo "Error: database not running"
    exit 1
fi

# get COMPOSE_PROJECT_NAME (see .env)
compose_project_name="$(
    docker inspect "$(docker-compose ps --quiet db)" \
        --format '{{ index .Config.Labels "com.docker.compose.project"}}'
)"
dump_filename="psql_dump-$(date --iso-8601=minutes)-${compose_project_name}"

for service_name in $COMPOSE_PROJECT_SERVICES; do
    if [ $service_name = fhir ]; then
        # HAPI db name does not match service name (fhir)
        service_name=hapifhir
    fi
    dump_db $service_name $dump_filename
done
