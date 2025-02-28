#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
gunicorn -w 4 \
         -b 0.0.0.0:8000 \
         --access-logfile - \
         --error-logfile - \
         src.wsgi:app 