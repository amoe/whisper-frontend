#! /bin/sh

set -eu

db_name=$(crudini --get whisper-frontend.ini main db_name)
db_username=$(crudini --get whisper-frontend.ini main db_username)
db_password=$(crudini --get whisper-frontend.ini main db_password)
db_hostname=$(crudini --get whisper-frontend.ini main db_hostname)

PGPASSWORD="$db_password" psql -U "$db_username" -h "$db_hostname" "$db_name"
