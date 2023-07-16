#!/bin/bash

function setup_package() {
    file_name='_package_libs.txt'
    while read line; do
    # reading each line
    echo "$line"
    done < $file_name
}

function runserver() {
    python manage.py migrate
    python manage.py loaddata /_setup/db_init/my_dump.json
    python manage.py runserver 0.0.0.0:8000
}

#setup_package
runserver