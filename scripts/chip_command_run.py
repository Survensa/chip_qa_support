import os
import sys
from datetime import datetime
import subprocess
import yaml 

# chip-tool path
homedir = os.path.join(os.path.expanduser('~'), "chip_command_run","config.yaml")
with open(homedir,'r') as file:
    yaml_info = yaml.safe_load(file)
    build = yaml_info["chip_tool_directory"]

# Folder Path
path = "../commands"

# Change the directory
os.chdir(path)

# Fn to run chip commands in terminal
def run_command(commands, testcase):
    file_path = os.path.join(os.path.expanduser('~'), build)  # Chip tool run directory
    save_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "BackendLogs")  # Chip tool log directory
    os.chdir(file_path)
    date = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
    while "" in commands:
        commands.remove("")
    for i in commands:
        with open(f"{save_path}/{testcase}-{date}.txt", 'a') as cluster_textfile:
            print(testcase, i)
            cluster_textfile.write('\n' + '\n' + i + '\n' + '\n')
        # subprocess module is used to open, append logs and run command in the terminal
        subprocess.run(i, shell=True, text=True, stdout=open(f"{save_path}/{testcase}-{date}.txt", "a+"))
    print(f"---------------------{testcase} - Executed----------------------")


# Read text File
def read_text_file(file_path):
    testsite_array = []
    filterCommand = []
    with open(file_path, 'r') as f:
        for line in f:
            testsite_array.append(line)
        filter_command = filter_commands(testsite_array)
        for command in filter_command:
            for com in command:
                # Separate testcase name from the array of commands
                if "#" in com:
                    testcase = com.split()[1]
                else:
                    filterCommand.append(com)
            run_command(filterCommand, testcase)
            filterCommand = []


# Fn to filter only commands form txt file
def filter_commands(commands):
    newcommand = []
    for command in commands:
        if "\n" in command:
            command = command.replace("\n", "")
        if "$" not in command:
            newcommand.append(command)
    size = len(newcommand)
    # Remove all the end in the array
    idx_list = [idx + 1 for idx, val in
                enumerate(newcommand) if val.lower() == "end"]
    res = [newcommand[i: j] for i, j in
           zip([0] + idx_list, idx_list +
               ([size] if idx_list[-1] != size else []))]
    newRes = []
    for i in res:
        i.pop()
        newRes.append(i)
    return newRes


# iterate through all file
for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands",
                                 file)  # Chip tool commands txt directory
        # call read text file function
        read_text_file(file_path)
