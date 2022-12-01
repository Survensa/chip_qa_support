echo "Hello..!" $USER
sleep 2
echo
read -p "Confirm wheather you have updated chip_tool_directory in build_config.json(Y/N)?" -n 1 -r
sleep 10
echo
if [[ ! $REPLY =~ ^[Yn]$ ]]
then
	sleep 2
	echo
	echo " These are the list of commands you have choosed for execution :"
	echo
	ls -1 ~/chip_command_run/commands/
	echo
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
		cd ~/chip_command_run/scripts/
		python3 chip_command_run.py
	fi
	echo
	echo "Execution completed"
	echo
	echo "Get execution logs from Backendlosg directory"
	exit
else
	echo
	sleep 5
	echo "Execution Aborted please update chip_tool_directory in build_config.json"
	echo
	sleep 2
	echo "Bye...!"
	exit
fi	
