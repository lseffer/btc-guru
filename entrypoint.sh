#! /bin/bash

set -e

if [ "$APP_COMPONENT" = "jobrunner" ]; then
    echo 'Initializing database ...'
    python $HOME/btc_guru/etl/initialize_database.py

    echo 'Starting jobrunner'
    while true; do
        echo 'hello'
        sleep 30
    done
fi

if [ "$APP_COMPONENT" = "webserver" ]; then
    echo 'Starting webserver'
    gunicorn -w 3 -k gevent -b 0.0.0.0:5001 webserver:app
fi
