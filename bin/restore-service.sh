#!/bin/sh -e

cmdname="$(basename "$0")"
bin_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="$(readlink -f ${bin_path}/..)"


usage() {
    cat << USAGE >&2
Usage:
    $cmdname [--help|-h] compose_project_dir compose_project_service database_dump


    Application restore script
    Load application database

    compose_project_dir
        docker-compose project directory name eg femr, logs, cosri
    compose_project_service
        service name to restore
    database_dump
        filepath to database dump to load

USAGE
    exit 1
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

COMPOSE_PROJECT_DIR="$1"
COMPOSE_PROJECT_SERVICE="$2"
SQL_DUMP="$3"
if [ ! -s "$SQL_DUMP" ]; then
    echo "Error: ${SQL_DUMP} is not non-zero file"
    exit 1
fi

# handle database names that do not match service names
DATABASE_SERVICE_NAME=db
DB_NAME="$COMPOSE_PROJECT_SERVICE"
if [ $COMPOSE_PROJECT_DIR = logs ]; then
    DATABASE_SERVICE_NAME=postgres
    DB_NAME=app_db
fi
if [ $COMPOSE_PROJECT_SERVICE = fhir ]; then
    DB_NAME=hapifhir
fi



restore_sqldump() {
    # restore a deployment from a given SQL dump file path and DB service name
    local db_service_name="$1"
    local db_name="$2"
    local sqldump_path="$3"
    local postgres_user="$(docker-compose exec -T $db_service_name printenv POSTGRES_USER)"


    echo "Stopping every service except database..."
    docker stop $(docker-compose ps --quiet | grep -v $(docker-compose ps --quiet $db_service_name))

    echo "Dropping existing $db_name DB..."
    docker-compose exec $db_service_name \
        dropdb --username $postgres_user $db_name

    echo "Creating empty $db_name DB..."
    docker-compose exec $db_service_name \
        createdb --username $postgres_user $db_name

    echo "Loading SQL dumpfile: ${sqldump_path}..."
    # Disable pseudo-tty allocation
    docker-compose exec -T $db_service_name \
        psql --dbname $db_name --username $postgres_user < "${sqldump_path}"
    echo "Loaded SQL dumpfile"
}


get_compose_project() {
    # get path to first active docker-compose project, given project name
    local repo_path="$1"
    local compose_project_dir_name="$2"
    # assume project is in use based on presence of .env file
    echo "$(dirname $(find "$repo_path" -path "*/$compose_project_dir_name/.env" -print -quit))"
}


docker_compose_directory="$(get_compose_project "$repo_path" "$COMPOSE_PROJECT_DIR")"

# docker-compose commands must be run in the same directory as docker-compose.yaml
cd "${docker_compose_directory}"

if [ -z "$(docker-compose ps --quiet $DATABASE_SERVICE_NAME)" ]; then
    >&2 echo "Error: database not running"
    exit 1
fi

restore_sqldump $DATABASE_SERVICE_NAME $DB_NAME $SQL_DUMP
