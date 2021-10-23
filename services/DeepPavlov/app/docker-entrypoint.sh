#!/bin/bash

ls -la
celery --app app.celery worker -P solo &
python app.py 

# ls /home/user/.cache/torch/sentence_transformers/

# python -m http.server 8000