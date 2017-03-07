#!/bin/bash

# TODO: finish this

if [ -z "${this}" ]; then declare -xr this="${BASH_SOURCE[0]:-$0}"; fi
if [ -z "${here}" ]; then declare -xr here="$(cd "$(dirname "${this}")" && pwd)"; fi
if [ -z "${project_path}" ]; then declare -xr project_path="$(cd "${here}/.." && pwd)"; fi
if [ -z "${module_path}" ]; then declare -xr module_path="${project_path}/${python_module_name}"; fi;
if [ -z "${alembic_conf_path}" ]; then declare -xr alembic_conf_path="${module_path}/migrations/alembic.ini"; fi;


main_app_root_domain="bellyfeel.io"

main_app_name_lowercase="bellyfeel"
main_app_name_uppercase="BELLYFEEL"
main_app_name_camelcase="BellyFeel"
main_app_name_python_class_prefix="Bellyfeel"

main_python_module_name="bellyfeel"


# original="$1"
# replacement="$2"

# echo "Replacing $original with $replacement"
# egrep -r $original * | cut -d: -f1 | uniq | xargs gsed -i "s,$original,$replacement,g"

# if [ -z $3 ]; then
# original=`echo $original | tr '[:lower:]' '[:upper:]'`
# replacement=`echo $replacement | tr '[:lower:]' '[:upper:]'`
# echo "Replacing $original with $replacement"
# egrep -r $original * | cut -d: -f1 | uniq | xargs gsed -i "s,$original,$replacement,g"

# original=`echo $original | tr '[:upper:]' '[:lower:]'`
# replacement=`echo $replacement | tr '[:upper:]' '[:lower:]'`
# echo "Replacing $original with $replacement"
# egrep -r $original * | cut -d: -f1 | uniq | xargs gsed -i "s,$original,$replacement,g"
# fi;
