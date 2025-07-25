#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start gunicorn
gunicorn --bind=0.0.0.0:$PORT project.wsgi
