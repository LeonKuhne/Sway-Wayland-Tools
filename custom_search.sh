echo "hello"

if [ "$1" = "bookmark" ]; then
    NAME=$(echo "" | bemenu -p "Bookmark name:")
    URL=$()
    echo -e "bookmarking page... $NAME"
    echo -e "$NAME $URL"
else
    APP=$(echo -e "$(ls /usr/share/applications)\n$(echo 'daddy')" | awk -F '.desktop' ' { print $1 }' | bemenu)
    echo $APP
    swaymsg exec $APP
fi


