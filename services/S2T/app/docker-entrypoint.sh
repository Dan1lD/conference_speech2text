#!/bin/bash

celery --app app.celery worker -P solo &
python app.py

