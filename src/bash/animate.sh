#!/bin/bash

while true
do
   for wallpaper in ./img_out/*; do
      xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitoreDP-1/workspace0/last-image --set "${PWD}/${wallpaper}"
      echo "$wallpaper"
      sleep 0.067
   done
   if [ -f ./temp/noanimate ]; then
      xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitoreDP-1/workspace0/last-image --set "${PWD}/img_out/wallpaper0.png"
      echo "no animate"
      exit 1
   fi
done

