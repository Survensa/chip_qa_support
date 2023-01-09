#! /usr/bin/env bash

echo "Hello . . . !" $USER
read -p "Confirm wheather you have updated chip_tool_directory in config.yaml (Y/N)?" ANSWER1
if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]
then
	echo
	sleep 2
	echo " These are the list of commands you have choosed for execution :"
	echo
	ls -1 ~/chip_command_run/commands/
	echo
	read -p "Confirm wheather the list of commands can be executed (Y/N)?" ANSWER2
	if [ "$ANSWER2" == "Y" ] || [ "$ANSWER2" == "y" ]
	then
		echo
		echo "Your Execution Starts here . . ."
		cd ~/chip_command_run/scripts/
		python3 chip_command_run.py
		echo
		echo "Execution completed . . .  Get execution logs from Backendlosg directory"
		exit
	elif [ "$ANSWER2" == "N" ] || [ "$ANSWER2" == "n" ]
	then
		echo
		echo "Execution Aborted"
		exit
	else
		echo
		echo "INVALID INPUT . . . Retry again"
		exit
	fi
elif [ "$ANSWER1" == "N" ] || [ "$ANSWER1" == "n" ]
then
	echo
	echo "Execution Aborted . . . Please update chip_tool_directory in config.yaml"
	exit
else
	echo
	echo "INVALID INPUT . . . Retry again"
	exit
fi
