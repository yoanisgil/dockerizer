#!/bin/bash
DJANGODIR=/webapp/deploy          		# Django project directory

cd $DJANGODIR
test -f $DJANGODIR/requirements.txt && pip install -r requirements.txt
exit 0
