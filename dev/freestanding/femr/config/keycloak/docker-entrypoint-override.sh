#!/bin/sh
set -eu

repo_path="$(cd "$(dirname "$0")" && pwd)"
cmdname="$(basename "$0")"

usage() {
    cat << USAGE >&2
Usage:
    $cmdname command

    Docker entrypoint script
    Wrapper script that executes docker-related tasks before running given command

USAGE
    exit 1
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi


# update templated JSON files before start

update_config() {
    # render environment-variable-templated config files with current environment (mimic `envsubstr`)
    local config_file="$1"

    printenv | cut -d = -f 1 | grep '^__KEYCLOAK' | while read envvar_name; do
        local envvar_value="$(printenv "$envvar_name" || true)"
        grep -q "\${$envvar_name}" $config_file || continue

        sed -i "s|\${$envvar_name}|$envvar_value|g" "$config_file"
        echo updated $envvar_name in $config_file
    done
}

cp "${__KEYCLOAK_INPUT_CONFIG}" "${__KEYCLOAK_OUTPUT_CONFIG}"
update_config "${__KEYCLOAK_OUTPUT_CONFIG}"


echo $cmdname complete
echo executing given command $@
exec "$@"
