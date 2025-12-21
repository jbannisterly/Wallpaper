#!/bin/bash
BACKGROUND_PATH="out/output"

while true
do
   python ./src/wallpaper.py
   xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitoreDP-1/workspace0/last-image --set "${PWD}/${BACKGROUND_PATH}.png"
   sleep 0.1
done

