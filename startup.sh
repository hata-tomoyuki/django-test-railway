#!/bin/bash

echo "Starting Django application..."

# マイグレーションを実行
echo "Running migrations..."
python manage.py migrate

# 静的ファイルを収集
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Gunicornでアプリケーションを起動
echo "Starting Gunicorn..."
gunicorn project.wsgi --bind=0.0.0.0:$PORT --log-file -
