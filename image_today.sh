QUERY=$(date +"%A, %B %d")

# consider using '-R day' flag to get images from today :D
~/.tools/googliser.sh -p $QUERY -L -a wide -m 4mp -n 1 -o /data/Downloads #nothing should go to downloads, -o uses local dir
URL=$(head -n 1 ./download.links.list)
echo $URL
wget -O /data/Downloads/image.today $URL
rm ./download.links.list

# set the backgrounds
sway output DVI-D-1 bg /data/Downloads/image.today fill
sway output DVI-D-2 bg /data/Downloads/image.today fill
sway output HDMI-A-1 bg /data/Downloads/image.today fill
