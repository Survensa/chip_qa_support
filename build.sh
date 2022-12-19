#! /usr/bin/env bash

echo "Hello..!" $USER
sleep 2
echo
read -p "Confirm wheather you have updated config.yaml inputs (Y/N)?" ANSWER1
echo
if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]
then
    echo
    sleep 2
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
