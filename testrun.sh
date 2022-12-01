#! /usr/bin/env bash
echo "Hello..!" $USER
sleep 2
echo
echo " These are the list of commands you have choosed for execution :"
echo
ls -1 commands/
read -p "Confirm wheather the list of commands can be executed (Y/N)?" -n 1 -r
sleep 10
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo
    sleep 5
    echo "Abort Execution"
    echo
    sleep 2
    echo "Bye...!"
    exit
else
    echo
    sleep 5
    echo "Your Execution Starts here..."
    cd scripts/
    python chip_command_run.py
fi
echo
echo "Execution completed"
echo
echo "Get execution logs from Backendlosg directory"
