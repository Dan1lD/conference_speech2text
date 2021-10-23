#!/bin/bash

python /app/manage.py collectstatic --noinput

# sleep .10
# python /django/manage.py migrate

uwsgi --ini /app/uwsgi.ini
