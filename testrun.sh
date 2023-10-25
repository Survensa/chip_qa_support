#! /usr/bin/env bash

echo "Hello . . . !" $USER
read -p "Confirm whether you have updated the Execution Section in config.yaml (Y/N)?" ANSWER1
if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]
then
    echo
    cd ~/chip_command_run/scripts/
    python3 chip_command_run.py
    exit
elif [ "$ANSWER1" == "N" ] || [ "$ANSWER1" == "n" ]
then
    echo
    echo "Execution Aborted . . . Please update the Execution Section in config.yaml"
    exit
else
    echo
    echo "INVALID INPUT . . . Retry again"
    exit
fi
