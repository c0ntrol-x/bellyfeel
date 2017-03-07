#!/bin/bash

LOGFILE_PATH=online-check.log
declare -a URLS
URLS+=( "https://bellyfeel.io/.check" )
URLS+=( "https://bellyfeel.io/dist/css/admin.css" )
URLS+=( "https://bellyfeel.io/dist/css/bootstrap.min.css" )
URLS+=( "https://bellyfeel.io/dist/css/font-awesome.min.css" )
URLS+=( "https://bellyfeel.io/dist/js/jquery.min.js" )
URLS+=( "https://bellyfeel.io/in" )

rm -f "${LOGFILE_PATH}"

for url in ${URLS[*]}; do
    echo -ne "\033[1;30mchecking \033[1;37m'${url}'\033[1;30m...\033[0m"
    if curl -s "${url}" >> "${LOGFILE_PATH}"; then
        echo -e "\033[1;32mOK\033[0m"
    else
        echo -e "\033[1;31mFailed\033[0m"
        cat "${LOGFILE_PATH}"
        exit 1
    fi
done

echo
