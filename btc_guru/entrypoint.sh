#! /bin/bash

set -e

echo 'Initializing database ...'
python $HOME/btc_guru/initialize_database.py

echo 'Starting main process ...'
while true; do
    echo 'hello'
    sleep 30
done
