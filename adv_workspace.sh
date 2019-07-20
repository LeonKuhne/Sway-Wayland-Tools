workspace=$(swaymsg -r -t get_workspaces | grep "name" | sed 's/\s*"name": "//g' | sed 's/",//g' | bemenu)

case $1 in
	'select')
		sway workspace $workspace
	;;
	'rename')
		sway workspace $workspace
		newName=$(echo '' | bemenu)
		sway rename workspace $workspace to $newName
	;;
	'move')
		sway workspace $workspace
		output=$(swaymsg -r -t get_outputs | grep "name" | sed 's/\s*"name": "//g' | sed 's/",//g' | bemenu)
		sway move workspace to output $output
	;;
esac
