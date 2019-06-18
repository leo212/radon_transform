#!/bin/sh
apt-get update
apt-get -y install libgtk2.0-dev
python manage.py runserver
