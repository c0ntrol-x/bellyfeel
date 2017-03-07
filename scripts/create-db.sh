#!/bin/bash

python_module_name="bellyfeel"

if [ -z "${this}" ]; then declare -xr this="${BASH_SOURCE[0]:-$0}"; fi
if [ -z "${here}" ]; then declare -xr here="$(cd "$(dirname "${this}")" && pwd)"; fi
if [ -z "${project_path}" ]; then declare -xr project_path="$(cd "${here}/.." && pwd)"; fi
if [ -z "${module_path}" ]; then declare -xr module_path="${project_path}/${python_module_name}"; fi;
if [ -z "${alembic_conf_path}" ]; then declare -xr alembic_conf_path="${module_path}/migrations/alembic.ini"; fi;
declare -a MYSQL_CMD
declare -x MYSQL_USER
declare -x MYSQL_PASSWORD
declare -a MYSQL_DATABASES

MYSQL_DATABASES+=( "bellyfeeldb" )
MYSQL_USER="${USER}"
MYSQL_ROOT_PASSWORD=""
MYSQL_PASSWORD="1n5ECUR3_${USER}-p45Sw0rD"
MYSQL_IDENTIFIED_BY=""
sql_bin="$(which mysql)"

MYSQL_CMD+=( "${sql_bin}" )
MYSQL_CMD+=( "-uroot" )

if [ -n "${MYSQL_PASSWORD}" ]; then
    MYSQL_IDENTIFIED_BY="IDENTIFIED BY '${MYSQL_PASSWORD}'"
fi

if [ -n "${MYSQL_ROOT_PASSWORD}" ]; then
    MYSQL_CMD+=( "--password='${MYSQL_ROOT_PASSWORD}'" )
fi


function create-mysql-database() {
    db_name="${1}"
    ${MYSQL_CMD[*]} <<EOF
DROP DATABASE IF EXISTS ${db_name};
CREATE DATABASE IF NOT EXISTS ${db_name};
CREATE USER IF NOT EXISTS '${USER}'@'localhost'
  IDENTIFIED BY '${MYSQL_USER}'
  PASSWORD EXPIRE INTERVAL 180 DAY;
GRANT ALL PRIVILEGES ON ${db_name}.* TO ${USER}@'%' ${MYSQL_IDENTIFIED_BY};
EOF
    return $?
}


function run-migrations() {
    "$(which alembic)" -c "${alembic_conf_path}" upgrade head
    return $?
}

set -e

for db_name in ${MYSQL_DATABASES[*]}; do
    create-mysql-database "${db_name}"
done

run-migrations
echo
echo '------------------------------------'
echo
echo "Take note of your local credentials:"
echo "MYSQL_USER: ${MYSQL_USER}"
echo "MYSQL_PASSWORD: ${MYSQL_PASSWORD}"
echo "MYSQL_DATABASES: ${MYSQL_DATABASES[*]}" | tr '[:space:]' '\n'
