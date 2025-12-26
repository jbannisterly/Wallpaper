#!/bin/bash

while true
do
    python ./src/python/wallpaper.py
    sleep 10
    if [ -f ./temp/lowpower ]; then
        sleep 290
    fi
    if [ -f ./temp/nogenerate ]; then
        echo "no generate"
        exit 1
    fi
done

