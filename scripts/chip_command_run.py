import os
import sys
import subprocess
import yaml
import re
import argparse
from datetime import datetime
from dataclasses import dataclass, fields

@dataclass
class Cluster:
    cluster_paths = {
        "TVOCCONC": "../commands/Total_Volatile_Organic_Compounds_Concentration_Measurement.txt",
        "NDOCONC": "../commands/Nitrogen_Dioxide_Concentration_Measurement.txt",
        "CC": "../commands/Color_Control.txt",
        "LUNIT": "../commands/Unit_localization.txt",
        "FLDCONC": "../commands/Formaldehyde_Concentration_Measurement.txt",
        "SWTCH": "../commands/Switch.txt",
        "BRBINFO": "../commands/Bridged_Device_Basic_Information.txt",
        "BIND": "../commands/Binding.txt",
        "ULABEL": "../commands/User_Lable.txt",
        "PMICONC": "../commands/PM2.5_Concentration_Measurement.txt",
        "SMOKECO": "../commands/Smoke_and_CO_Alarm.txt",
        "DISHM": "../commands/Dishwasher_Mode_Cluster.txt",
        "FLABEL": "../commands/Fixed_Lable.txt",
        "DRLK": "../commands/Door_lock.txt",
        "ACFREMON": "../commands/Activated_Carbon_Filter_Monitoring.txt",
        "TSTAT": "../commands/Thermostat.txt",
        "DESC": "../commands/Descriptor_Cluster.txt",
        "MC": "../commands/Media.txt",
        "CDOCONC": "../commands/Carbon_Dioxide_Concentration_Measurement.txt",
        "PSCFG": "../commands/Power_Source_Configuration.txt",
        "DGETH": "../commands/Ethernet_Diag.txt",
        "DGSW": "../commands/Software_Diag.txt",
        "HEPAFREMON": "../commands/HEPA_Filter_Monitoring.txt",
        "RVCCLEANM": "../commands/RVC_Clean_Mode.txt",
        "PRS": "../commands/Pressure_measurement.txt",
        "I": "../commands/Identify.txt",
        "DGTHREAD": "../commands/Thread_diag.txt",
        "BOOL": "../commands/Boolean.txt",
        "TSUIC": "../commands/Thermostat_User.txt",
        "LCFG": "../commands/Localization_Configuration_cluster.txt",
        "WNCV": "../commands/Window_Covering.txt",
        "BINFO": "../commands/Basic_Information.txt",
        "OCC": "../commands/OccupancySensing.txt",
        "DGWIFI": "../commands/Wifi_Diag.txt",
        "GRPKEY": "../commands/Group_Communication.txt",
        "RH": "../commands/Relative_Humidity_Measurement_Cluster.txt",
        "PS": "../commands/Power_Source_Cluster.txt",
        "LTIME": "../commands/Time_Format_localization.txt",
        "G": "../commands/Groups.txt",
        "LWM": "../commands/Laundry_Washer_Mode.txt",
        "PMHCONC": "../commands/PM1_Concentration_Measurement.txt",
        "PCC": "../commands/pump_configuration.txt",
        "ACL": "../commands/Access_Control.txt",
        "RVCRUNM": "../commands/RVC_Run_Mode.txt",
        "RNCONC": "../commands/Radon_Concentration_Measurement.txt",
        "FLW": "../commands/Flow_Measurement_Cluster.txt",
        "MOD": "../commands/Mode_Select.txt",
        "LVL": "../commands/Level_Control.txt",
        "AIRQUAL": "../commands/Air_Quality.txt",
        "PMKCONC": "../commands/PM10_Concentration_Measurement.txt",
        "TMP": "../commands/Temperature_Measurement_Cluster.txt",
        "OZCONC": "../commands/Ozone_Concentration_Measurement.txt",
        "FAN": "../commands/Fan_Control.txt",
        "OO": "../commands/OnOff.txt",
        "CMOCONC": "../commands/Carbon_Monoxide_Concentration_Measurement.txt",
        "TCCM": "../commands/Refrigerator_And_Temperature_Controlled_Cabinet_Mode.txt",
        "DGGEN": "../commands/Gendiag.txt",
        "ILL": "../commands/Illuminance_Measurement_Cluster.txt",
        # Add other cluster paths here
    }

clusters = fields(Cluster)
cluster_names = [field.name for field in clusters]

# Parse command-line arguments
parser = argparse.ArgumentParser(description='cluster name')
parser.add_argument('-c', '--cluster', nargs='+', help='name of the cluster', choices=cluster_names, default=False)
args = parser.parse_args()

# Load configuration from YAML file
config_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "config.yaml")
with open(config_path, 'r') as config_file:
    yaml_info = yaml.safe_load(config_file)
    build = yaml_info.get("chip_tool_directory")

# Define regular expressions
pattern1 = re.compile(r'(CHIP:DMG|CHIP:TOO)(.*)')
pattern2 = re.compile(r'^\./chip-tool')

# Function to process log files and save them
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

# Function to run chip commands in terminal
def run_command(commands, testcase):
    file_path = os.path.join(os.path.expanduser('~'), build)
    save_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "BackendLogs")
    os.chdir(file_path)
    date = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
    commands = [c for c in commands if c != ""]  # Remove empty commands
    for i in commands:
        with open(f"{save_path}/{testcase}-{date}.txt", 'a') as cluster_textfile:
            print(testcase, i)
            cluster_textfile.write('\n' + '\n' + i + '\n' + '\n')
        # Use subprocess to run the command in the terminal and append logs
        subprocess.run(i, shell=True, text=True, stdout=open(f"{save_path}/{testcase}-{date}.txt", "a+"))

    # Process the log file immediately after running the commands
    input_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "BackendLogs")
    output_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs", "ExecutionLogs")
    process_log_files(input_directory, output_directory)
    print(f"---------------------{testcase} - Executed----------------------")

# Function to filter only commands from txt file
def filter_commands(commands):
    filtered_commands = [c.strip() for c in commands if "$" not in c]
    return [filtered_commands[i: j] for i, j in zip([0] + [i+1 for i, c in enumerate(filtered_commands) if c.lower() == "end"], 
                                                      [i for i, c in enumerate(filtered_commands) if c.lower() == "end"])]

# Function to read text files
def read_text_file(file_path):
    with open(file_path, 'r') as f:
        testsite_array = f.readlines()
    
    filter_command = filter_commands(testsite_array)
    for command in filter_command:
        testcase = None
        for com in command:
            if "#" in com:
                testcase = com.split()[1]
            else:
                testcase = None
        run_command(command, testcase)

# Function to process all files
def process_all_files():
    for file in os.listdir("../commands"):
        if file.endswith(".txt"):
            file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands", file)
            read_text_file(file_path)

if __name__ == "__main":
    selected_clusters = args.cluster

    if not selected_clusters:
        selected_clusters = [clus for clus in cluster_names if yaml_info.get(clus) == 'Y']

    if selected_clusters:
        for cluster_name in selected_clusters:
            file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands", Cluster.cluster_paths[cluster_name])
            read_text_file(file_path)
    else:
        process_all_files()
