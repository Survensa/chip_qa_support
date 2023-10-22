#! /usr/bin/env bash

echo "Hello . . . !" $USER
read -p "Confirm wheather you have updated chip_tool_directory and  in config.yaml (Y/N)?" ANSWER1
if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]
then
	echo
	echo "Your Execution Starts here . . ."
	cd ~/chip_command_run/scripts/
	python3 chip_command_run.py
	echo
	echo "Execution completed . . .  Logs are ready for validation in logs/validation_logs directory"
	exit
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
