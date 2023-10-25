import os
import sys
from datetime import datetime
import subprocess
import yaml
import re
import argparse
from dataclasses import dataclass, fields
from chip_command_run import Cluster, filter_commands , read_text_file
import threading
import json
from fabric import Connection
import time
from invoke import UnexpectedExit
import invoke.exceptions

clusters = fields(Cluster)

cluster_name = [field.name for field in clusters]

# Parse command-line arguments
parser = argparse.ArgumentParser(description='cluster name')

parser.add_argument('-c','--cluster', nargs='+',help='name of the cluster',choices= cluster_name,default= False)
parser.add_argument('-p','--pairing',help='Auto-pairing function', default= True)
args = parser.parse_args()

# Load configuration from YAML file
homedir = os.path.join(os.path.expanduser('~'), "chip_command_run", "config.yaml")
with open(homedir, 'r') as file:
    yaml_info = yaml.safe_load(file)
    build = yaml_info["chip_tool_directory"]



# Define regular expressions
pattern1 = re.compile(r'(CHIP:DMG|CHIP:TOO)(.*)')
pattern2 = re.compile(r'^\./chip-tool')
pattern3 = re.compile(r'avahi-browse')
testcase = ""


# Folder Path
path = os.path.join(os.getcwd(),"../commands")

# Change the directory
os.chdir(path)

# Function to factory reset the dut
def factory_reset( data ):

        ssh = Connection(host= data["host"], user=data["username"], connect_kwargs={"password": data["password"]})


        # Executing the  'ps aux | grep process_name' command to find the PID value to kill
        command = f"ps aux | grep {data['command']}"
        pid_val = ssh.run(command, hide=True)

        pid_output = pid_val.stdout
        pid_lines = pid_output.split('\n')
        for line in pid_lines:
            if data["command"] in line:
                pid = line.split()[1]
                conformance = line.split()[7]
                if conformance == 'Ssl':
                    kill_command = f"kill -9 {pid}"
                    ssh.run(kill_command)


        ssh.close()

#Function to advertise the dut
def advertise():
        
        cd = os.getcwd()
        rpi_path = os.path.join(cd,"../scripts/rpi.json") 

        with open( rpi_path, "r") as f:
            data = json.load(f)


        ssh = Connection(host= data["host"], user=data["username"], connect_kwargs={"password": data["password"]})

        path = data["path"]
        ssh.run('rm -rf /tmp/chip_*')

        try:
            log = ssh.run('cd ' + path + ' && ' + data["command"], warn=True, hide=True, pty=False)
        except UnexpectedExit as e:
            if e.result.exited == -1:
                None
            else:
                raise

        #self.start_logging(log)
        ssh.close()
        logpath = os.path.join(cd,"../Logs/BackendLogs") 
        date = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
        with open(f"{logpath}/{testcase}dut-{date}.txt", 'a') as f:
            f.write(log.stdout)
        return True


# Function to assign the testcase name to the dut-side log
def testcasename(tc):
    global testcase
    testcase = tc
    return None


# Fn to process log files and save them
def process_log_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)
            avahi = False

            with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
                for line in input_file:
                    line = line.strip()
                    match1 = pattern1.search(line)
                    match2 = pattern2.search(line)
                    match3 = pattern3.search(line)
                    if match1:
                        chip_text = match1.group(1).strip()
                        trailing_text = match1.group(2).strip()
                        output_line = f"{chip_text} {trailing_text}"
                        output_file.write(output_line + '\n')
                    elif match2:
                        output_file.write('\n' 'CHIP:CMD : ' + line + '\n\n')
                        avahi = False
                    elif match3:
                        output_file.write('\n' 'CHIP:CMD : ' + line + '\n')
                        avahi = True
                    elif avahi:
                        output_file.write( line + '\n')


# Function to scrap the manualcode from the log
def code():
    with open ("temp.txt", 'r') as f:
        for line in f:
            line = line.strip()
            match = re.search(r'Manual pairing code: \[(\d+)\]', line)
            if match:
                manualcode = match.group(1)
                return(str(manualcode))
            
    return False

    

# Fn to run chip commands in terminal
def run_command(commands, testcase):
    file_path = os.path.join(os.path.expanduser('~'), build)
    save_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "BackendLogs")
    testcasename(testcase)
    cd = os.getcwd()
    pair = args.pairing
    date = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
    manualcode = "34970112332"
    if pair :
        data = yaml_info.Dut_data
        factory_reset(data)
        thread = threading.Thread(target= advertise)
        thread.daemon = True
        thread.start()
        time.sleep(5)
        os.chdir(file_path)
        rebootcmd = "rm -rf /tmp/chip_*"
        subprocess.run(rebootcmd, shell=True, text=True, stdout= subprocess.PIPE, stderr=subprocess.PIPE)
        pairing_cmd = "./chip-tool pairing onnetwork 1 20202021"
        subprocess.run(pairing_cmd, shell=True, text=True, stdout= subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        os.chdir(file_path)

    while "" in commands:
        commands.remove("")
    for i in commands:
        log_filename = f"{testcase}-{date}.txt"
        log_file_path = os.path.join(save_path, log_filename)
        with open(log_file_path, 'a') as cluster_textfile:
            print(testcase, i)
        # subprocess module is used to open, append logs and run command in the terminal
            if "open-commissioning-window" in i:
                cluster_textfile.write('\n' + '\n' + i + '\n' + '\n')

            if "open-basic-commissioning-window" in i:
                manualcode = "34970112332"

            elif "{code}" in i:
                i = i.replace("{code}", manualcode)
                cluster_textfile.write('\n' + '\n' + i + '\n' + '\n')

            else:
                cluster_textfile.write('\n' + '\n' + i + '\n' + '\n')

        run = subprocess.run(i, shell=True, text=True, stdout= subprocess.PIPE, stderr=subprocess.PIPE)

        log = run.stdout
                
        with open("temp.txt", 'w') as f:
                    f.write(log)
        if "open-commissioning-window" in i:
            cod = code()
            if cod == False:
                None
            else:
                manualcode = cod

        with open(log_file_path, 'a') as cluster_textfile:
            cluster_textfile.write(log)

    if pair :
        factory_reset(data)
        time.sleep(5)
    
    # Process the log file immediately after running the commands
    output_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "ExecutionLogs")
    process_log_files(log_file_path, output_directory)
    os.chdir(cd)
    print(f"\n---------------------{testcase} - Executed----------------------")
    print(f"\nExecution log saved as {log_filename}")
    print(f"Validation log processed for {testcase}")
    print(f"\n****************************************************************")


if __name__ == "__main__":
    
    selected_clusters = args.cluster

    build_confirmation = input(f"\nConfirm the Chip-Tool Build Path: {build} (Y/Yes to confirm): ").strip().lower()

    if build_confirmation in ['y', 'yes']:

        if selected_clusters:
            None
        else:
            selected_clusters = ["CADMIN"]

        clusters_confirmation = input(f"\nProceed with selected Clusters {selected_clusters} for execution (Y/Yes to proceed): ").strip().lower()
        print(f"\n****************************************************************")

        if clusters_confirmation in ['y', 'yes']:
            if selected_clusters:
                for cluster_name in selected_clusters:
                    file = vars(Cluster)[cluster_name]
                    file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands", file)
                    read_text_file(file_path)
        else:
            print("Execution canceled.")

    else:
        print("Execution canceled.")
