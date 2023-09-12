import os
import sys
from datetime import datetime
import subprocess
import yaml
import re

pattern1 = re.compile(r'(CHIP:DMG|CHIP:TOO)(.*)')
pattern2 = re.compile(r'^\./chip-tool')

# chip-tool path
homedir = os.path.join(os.path.expanduser('~'), "chip_command_run", "config.yaml")
with open(homedir, 'r') as file:
    yaml_info = yaml.safe_load(file)
    build = yaml_info["chip_tool_directory"]

# Folder Path
path = "../commands"

# Change the directory
os.chdir(path)

# Fn to process log files and save them
def process_log_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)

            with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
                for line in input_file:
                    line = line.strip()
                    match1 = pattern1.search(line)
                    match2 = pattern2.search(line)
                    if match1:
                        chip_text = match1.group(1).strip()
                        trailing_text = match1.group(2).strip()
                        output_line = f"{chip_text} {trailing_text}"
                        output_file.write(output_line + '\n')
                    if match2:
                        output_file.write('\n' 'CHIP:CMD : ' + line + '\n\n')

# Fn to run chip commands in terminal
def run_command(commands, testcase):
    file_path = os.path.join(os.path.expanduser('~'), build)
    save_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "BackendLogs")
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
    
    # Process the log file immediately after running the commands
    input_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "BackendLogs")
    output_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "ExecutionLogs")
    process_log_files(input_directory, output_directory)

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

# Fn to filter only commands from txt file
def filter_commands(commands):
    newcommand = []
    for command in commands:
        if "\n" in command:
            command = command.replace("\n", "")
        if "$" not in command:
            newcommand.append(command)
    size = len(newcommand)
    # Remove all the "end" in the array
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

# iterate through all files
for file in os.listdir():
    # Check whether the file is in text format or not
    if file.endswith(".txt"):
        file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands",
                                 file)  # Chip tool commands txt directory
        # call read text file function
        read_text_file(file_path)
