#!/bin/bash

i="0"
while [ $i -lt 20 ]
do
grim -o DP-1 screenshot.png
firefox-nightly screenshot.png
ping -c 3 locahost
i=$[$i+1]
done
