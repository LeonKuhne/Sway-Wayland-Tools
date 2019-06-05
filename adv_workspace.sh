workspace=$(swaymsg -r -t get_workspaces | grep "name" | sed 's/\s*"name": "//g' | sed 's/",//g' | dmenu)

case $1 in
	'select')
		sway workspace $workspace
	;;
	'rename')
		sway workspace $workspace
		newName=$(echo '' | dmenu)
		sway rename workspace $workspace to $newName
	;;
	'move')
		sway workspace $workspace
		output=$(swaymsg -r -t get_outputs | grep "name" | sed 's/\s*"name": "//g' | sed 's/",//g' | dmenu)
		sway move workspace to output $output
	;;
esac
