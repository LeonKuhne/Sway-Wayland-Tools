#!/bin/sh
query="himom"
url="https://www.googleapis.com/customsearch/v1?q=${query}&num=1&start=1&key=AIzaSyBDGGKs-a8bINzP6jd_4u1qqBW7y4kNz38&cx=012781726598733212613%3Aao6yapeacdo&imgSize=large&filetype=jpg&tbm=isch"
wget -O /data/Downloads/searchtoday.json $url
imgurl=$(jq '.items[0].pagemap.cse_image[0].src' /data/Downloads/searchtoday.json)
echo $imgurl
#wget -O /data/Downloads/imagetoday.jpg $imgurl
