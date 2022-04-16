#!/bin/bash

script="$1"
run_script="python $script"
last_modified=""
echo $last_modified

while : ; do
  current_date=$(date -r $script)
  if [ "$last_modified" != "$current_date" ]; then
    echo "reloading"
    ps -ef | grep "$run_script"  | grep -v grep | awk -F" " 'system("kill  "$2"")'
    setsid $(eval $run_script) >/dev/null 2>&1 < /dev/null &
    last_modified=$current_date
  fi
  sleep 1
done
