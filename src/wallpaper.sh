#!/bin/bash
BACKGROUND_PATH="out/output"

while true
do
for i in $(seq 0 10);
do
   xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitoreDP-1/workspace0/last-image --set "${PWD}/${BACKGROUND_PATH}${i}.0.png"
   sleep 0.1
done
for i in $(seq 0 10);
do
   ii=$((10 - i))
   xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitoreDP-1/workspace0/last-image --set "${PWD}/${BACKGROUND_PATH}${ii}.0.png"
   sleep 0.1
done

done

