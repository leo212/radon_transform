#!/bin/sh
apt-get update
apt-get install libgtk2.0-dev
python manage.py runserver
