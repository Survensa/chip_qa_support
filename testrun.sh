#!/usr/bin/env bash

echo "Hello . . . !" $USER
echo
read -p "Confirm whether you have updated the Execution Section in config.yaml (Y/N)?" ANSWER1

if [ "$ANSWER1" == "Y" ] || [ "$ANSWER1" == "y" ]; then
    if [[ "$1" == "-c" && "$2" == "CADMIN" ]] || [[ "$1" == "--cluster" && "$2" == "CADMIN" ]]; then
        cd ~/chip_command_run/scripts/
        python3 chip_cadmin_command_run.py "${@:3}"
    else
        cd ~/chip_command_run/scripts/
        python3 chip_command_run.py "$@"
    fi
elif [ "$ANSWER1" == "N" ] || [ "$ANSWER1" == "n" ]; then
    echo
    echo "Execution Aborted . . . Please update the Execution Section in config.yaml"
else
    echo
    echo "INVALID INPUT . . . Retry again"
fi
exit
