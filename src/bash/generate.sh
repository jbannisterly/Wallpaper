#!/bin/bash

while true
do
    python ./src/python/wallpaper.py
    sleep 10
    if [ -f ./temp/nogenerate ]; then
        echo "no generate"
        exit 1
    fi
done

