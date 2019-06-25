ACTIVE_SINK=$(pacmd list-sinks | awk '/index:/{i++} /* index:/{print i; exit}')
pactl set-sink-volume $ACTIVE_SINK $@
