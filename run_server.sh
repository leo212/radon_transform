#!/bin/sh
apt-get update
apt-get -y install libglib2.0-0
python manage.py runserver
