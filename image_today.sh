#!/bin/bash

#source /home/x/.bash_profile
QUERY=$(date +"%A, %B %d")
NOUN=$(curl https://www.random-ize.com/noun/nou-f.php)
# consider using '-R day' flag to get images from today :D
/home/x/.tools/googliser.sh -p "$QUERY $NOUN" -L -a wide -m 4mp -n 1 -o /data/Downloads #nothing should go to downloads, -o uses local dir
URL=$(head -n 1 download.links.list)
wget -O /data/Downloads/image.today $URL
rm download.links.list

# get the current active socket
export SWAYSOCK=/run/user/$(id -u)/sway-ipc.$(id -u).$(pgrep -x sway).sock

# set the backgrounds
sway output DP-1 bg /data/Downloads/image.today fill
sway output DVI-D-1 bg /data/Downloads/image.today fill
sway output DVI-D-2 bg /data/Downloads/image.today fill
sway output HDMI-A-1 bg /data/Downloads/image.today fill
