import os
import sys
from datetime import datetime
import subprocess
import yaml
import re
import argparse
from dataclasses import dataclass, fields
from chip_command_run import Cluster
import threading
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
