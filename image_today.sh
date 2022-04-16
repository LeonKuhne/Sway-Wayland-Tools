#!/bin/bash
#source /home/x/.bash_profile

# need this for the cronjob
TOOLS=/home/x/Projects/tools
IMG_SAVE_DIR=/home/x/Pictures/today
IMG_URL_DIR=/home/x

# find the image
#QUERY=$(date +"%A, %B %d")
NOUN=$(curl https://www.random-ize.com/noun/nou-f.php)
NOUN2=$(curl https://www.random-ize.com/noun/nou-f.php)
/usr/local/bin/googliser -L -a wide -n 1 -R "day" -p "$NOUN $NOUN2" -o $IMG_SAVE_DIR
#/usr/local/bin/googliser -L -a wide -n 1 -o $IMG_DIR -R "day" -p "$NOUN" --random
#/usr/local/bin/googliser -L -a wide -m 4mp -n 1 -o $IMG_DIR -p "$QUERY $NOUN"
URL=$(head -n 1 ./image.links.list)

# save the image
echo "found url: $URL"
wget -O $IMG_SAVE_DIR/image.today $URL

# add the nouns
magick $IMG_SAVE_DIR/image.today -font DejaVuSans-Bold -fill black -pointsize "%[fx:w/25]" -gravity Center -draw "text 0,%[fx:(9*w)/(16*h)*(h/3)] '$NOUN $NOUN2'" $IMG_SAVE_DIR/image.today

rm $IMG_URL_DIR/image.links.list

# get the current active socket, for cronjob
export SWAYSOCK=/run/user/$(id -u)/sway-ipc.$(id -u).$(pgrep -x sway).sock

# show the background image
sway output DP-1 bg $IMG_SAVE_DIR/image.today fill
#sway output DVI-D-1 bg $IMG_SAVE_DIR/image.today fill
#sway output DVI-D-2 bg $IMG_SAVE_DIR/image.today fill
#sway output HDMI-A-1 bg $IMG_SAVE_DIR/image.today fill

# Split the background up into 4 pieces
#

# I stole these values from ~/.config/sway/config

# total screen image. The '^' stands for 'minimum values of width and height given, aspect ratio preserved'
#convert -gravity center -resize 4740x2340^ /home/x/Downloads/image.today /home/x/Downloads/image_today.png
# individual cropings
#convert -crop 1440x900+1600+0 /home/x/Downloads/image_today.png /home/x/Downloads/image_today_1.png
#convert -crop 1920x1080+0+960 /home/x/Downloads/image_today.png /home/x/Downloads/image_today_2.png
#convert -crop 900x1440+1920+900 /home/x/Downloads/image_today.png /home/x/Downloads/image_today_3.png
#convert -crop 1920x1080+2820+900 /home/x/Downloads/image_today.png /home/x/Downloads/image_today_4.png

# show the split background images
#sway output HDMI-A-1 bg /home/x/Downloads/image_today_1.png fill
#sway output DVI-D-2 bg /home/x/Downloads/image_today_2.png fill
#sway output DVI-D-1 bg /home/x/Downloads/image_today_3.png fill
#sway output DP-1 bg /home/x/Downloads/image_today_4.png fill
