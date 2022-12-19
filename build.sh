#! /usr/bin/env bash

echo "Hello..!" $USER
echo
read -p "Confirm wheather you have updated config.yaml inputs (Y/N)?" ANSWER1
if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]
then
    echo
    echo "Your build Starts here..."
    cd ~/chip_command_run/scripts/
    python3 chip_build.py
    echo
    echo "Check apps folder for successfull build"
    exit
elif [ "$ANSWER1" == "N" ] || [ "$ANSWER1" == "n" ]; then
    echo
    echo "Execution Aborted . . . Please update your inputs in config.yaml"
    exit
else
    echo
    echo "INVALID INPUT . . . Retry again"
    exit
fi
