#! /bin/bash

source ./cores-venv/bin/activate

rm -f ./db.sqlite3
rm -rf ./*/migrations/*

python3 manage.py makemigrations booking inventory live notices
python3 manage.py migrate
python3 manage.py createsuperuser

python3 manage.py runserver
