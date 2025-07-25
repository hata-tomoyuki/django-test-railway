#!/bin/bash

# マイグレーションを実行
python manage.py migrate

# 静的ファイルを収集
python manage.py collectstatic --noinput

# Gunicornでアプリケーションを起動
gunicorn project.wsgi --log-file -
