#!/bin/bash

NAME="app"                              # Name of the application
DJANGODIR=/webapp/deploy          		# Django project directory
SOCKFILE=/webapp/gunicorn.sock     		# we will communicte using this unix socket
NUM_WORKERS=4                           # how many worker processes should Gunicorn spawn

APPNAME=$(basename $(dirname $(find $DJANGODIR -maxdepth 2 -type f -name settings.py)))

DJANGO_SETTINGS_MODULE=$APPNAME.settings     # which settings file should Django use
DJANGO_WSGI_MODULE=$APPNAME.wsgi             # WSGI module name


echo "Starting $NAME as `whoami`"

# Activate the virtual environment
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

cd $DJANGODIR
python manage.py dockersetup --username admin --password admin --email gil.yoanis@gmail.com
python manage.py collectlayers --noinput

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --log-file=- \
  --error-logfile=- \
  --threads 4
