#! /usr/bin/env bash

echo "Hello..!" $USER
sleep 2
echo
read -p "Confirm wheather you have updated build_config.json inputs (Y/N)?:" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo
    sleep 5
    echo "Please update your inputs in build_config.json "
    echo
    sleep 2
    echo "Bye...!"
    exit
else
    echo
    sleep 5
    echo "Your build Starts here..."
    cd scripts/
    python chip_build.py
fi
echo
echo " Check apps folder for successfull buil "
