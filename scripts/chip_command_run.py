import os
import sys
from datetime import datetime
import subprocess
import yaml
import re
import argparse
from dataclasses import dataclass, fields

@dataclass
class Cluster:
    
    TVOCCONC : str = "../commands/Total_Volatile_Organic_Compounds_Concentration_Measurement.txt"
    NDOCONC : str = "../commands/Nitrogen_Dioxide_Concentration_Measurement.txt"
    CC : str = "../commands/Color_Control.txt"
    LUNIT : str = "../commands/Unit_localization.txt"
    FLDCONC : str = "../commands/Formaldehyde_Concentration_Measurement.txt"
    SWTCH : str = "../commands/Switch.txt"
    BRBINFO : str = "../commands/Bridged_Device_Basic_Information.txt"
    BIND : str = "../commands/Binding.txt"
    ULABEL : str = "../commands/User_Lable.txt"
    PMICONC : str = "../commands/PM2.5_Concentration_Measurement.txt"
    SMOKECO : str = "../commands/Smoke_and_CO_Alarm.txt"
    DISHM : str = "../commands/Dishwasher_Mode_Cluster.txt"
    FLABEL : str = "../commands/Fixed_Lable.txt"
    DRLK : str = "../commands/Door_lock.txt"
    ACFREMON : str = "../commands/Activated_Carbon_Filter_Monitoring.txt"
    TSTAT : str = "../commands/Thermostat.txt"
    DESC : str = "../commands/Descriptor_Cluster.txt"
    MC : str = "../commands/Media.txt"
    CDOCONC : str = "../commands/Carbon_Dioxide_Concentration_Measurement.txt"
    PSCFG : str = "../commands/Power_Source_Configuration.txt"
    DGETH : str = "../commands/Ethernet_Diag.txt"
    DGSW : str = "../commands/Software_Diag.txt"
    HEPAFREMON : str = "../commands/HEPA_Filter_Monitoring.txt"
    RVCCLEANM : str = "../commands/RVC_Clean_Mode.txt"
    PRS : str = "../commands/Pressure_measurement.txt"
    I : str = "../commands/Identify.txt"
    DGTHREAD : str = "../commands/Thread_diag.txt"
    BOOL : str = "../commands/Boolean.txt"
    TSUIC : str = "../commands/Thermostat_User.txt"
    LCFG : str = "../commands/Localization_Configuration_cluster.txt"
    WNCV : str = "../commands/Window_Covering.txt"
    BINFO : str = "../commands/Basic_Information.txt"
    OCC : str = "../commands/OccupancySensing.txt"
    DGWIFI : str = "../commands/Wifi_Diag.txt"
    GRPKEY : str = "../commands/Group_Communication.txt"
    RH : str = "../commands/Relative_Humidity_Measurement_Cluster.txt"
    PS : str = "../commands/Power_Source_Cluster.txt"
    LTIME : str = "../commands/Time_Format_localization.txt"
    G : str = "../commands/Groups.txt"
    LWM : str = "../commands/Laundry_Washer_Mode.txt"
    PMHCONC : str = "../commands/PM1_Concentration_Measurement.txt"
    PCC : str = "../commands/pump_configuration.txt"
    ACL : str = "../commands/Access_Control.txt"
    RVCRUNM : str = "../commands/RVC_Run_Mode.txt"
    RNCONC : str = "../commands/Radon_Concentration_Measurement.txt"
    FLW : str = "../commands/Flow_Measurement_Cluster.txt"
    MOD : str = "../commands/Mode_Select.txt"
    LVL : str = "../commands/Level_Control.txt"
    AIRQUAL : str = "../commands/Air_Quality.txt"
    PMKCONC : str = "../commands/PM10_Concentration_Measurement.txt"
    TMP : str = "../commands/Temperature_Measurement_Cluster.txt"
    OZCONC : str = "../commands/Ozone_Concentration_Measurement.txt"
    FAN : str = "../commands/Fan_Control.txt"
    OO : str = "../commands/OnOff.txt"
    CMOCONC : str = "../commands/Carbon_Monoxide_Concentration_Measurement.txt"
    TCCM : str = "../commands/Refrigerator_And_Temperature_Controlled_Cabinet_Mode.txt"
    DGGEN: str = "../commands/Gendiag.txt"
    ILL : str = "../commands/Illuminance_Measurement_Cluster.txt"

clusters = fields(Cluster)
cluster_name = [field.name for field in clusters]

# Parse command-line arguments
parser = argparse.ArgumentParser(description='cluster name')
parser.add_argument('-c','--cluster', nargs='+', help='name of the cluster', choices=cluster_name, default=False)
args = parser.parse_args()

# Load configuration from YAML file
config_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "config.yaml")
with open(config_path, 'r') as config_file:
    yaml_info = yaml.safe_load(config_file)
    build = yaml_info.get("chip_tool_directory")

# Define your regular expression patterns
pattern1 = re.compile(r'(CHIP:DMG|CHIP:TOO)(.*)')
pattern2 = re.compile(r'^\./chip-tool')

# Function to run chip commands and save logs
def run_command(commands, testcase, common_log_name):
    file_path = os.path.join(os.path.expanduser('~'), build)
    log_dir = os.path.join(os.path.expanduser('~'), "chip_command_run", "Logs")

    # Create a common log file name with the cluster name, date, and time
    common_log_file = f"{testcase}-{common_log_name}.txt"
    backend_log_path = os.path.join(log_dir, "BackendLogs", common_log_file)
    execution_log_path = os.path.join(log_dir, "ExecutionLogs", common_log_file)

    os.chdir(file_path)
    while "" in commands:
        commands.remove("")
    for i in commands:
        with open(backend_log_path, 'a') as log_file:
            print(testcase, i)
            log_file.write('\n' + '\n' + i + '\n' + '\n')
        
        # Execute the command and append logs to both backend and execution logs
        completed_process = subprocess.run(i, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Filter and write the lines matching pattern1 and pattern2
        with open(backend_log_path, 'a') as backend_log_file, open(execution_log_path, 'a') as execution_log_file:
            for line in completed_process.stdout.splitlines():
                if pattern1.match(line) or pattern2.match(line):
                    execution_log_file.write(line + '\n')
        
    print(f"---------------------{testcase} - Executed----------------------")

# Function to read text files
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

# Function to filter only commands from txt file
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

# Function to process all files
def process_all_files():
# iterate through all files
    for file in os.listdir():
    # Check whether the file is in text format or not
        if file.endswith(".txt"):
            file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands", file)  # Chip tool commands txt directory
            # call read text file function
            read_text_file(file_path)

if __name__ == "__main__":
    selected_clusters = args.cluster

    # Ask the user to confirm the Chip-Tool Build Path
    build_confirmation = input(f"Confirm the Chip-Tool Build Path: {build} (Y/Yes to confirm): ").strip().lower()

    if build_confirmation in ['y', 'yes']:
        if selected_clusters:
            None
        else:
            selected_clusters = []
            for clus in cluster_name:
                e = yaml_info[clus]
                if e in ['Y', 'Yes']:
                    selected_clusters.append(clus)

        # Ask the user to confirm the selected clusters for execution
        clusters_confirmation = input(f"Proceed with selected Clusters for execution: {selected_clusters} (Y/Yes to proceed): ").strip().lower()

        if clusters_confirmation in ['y', 'yes']:
            if selected_clusters:
                common_log_name = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
                for cluster_name in selected_clusters:
                    file = vars(Cluster)[cluster_name]
                    file_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands", file)
                    read_text_file(file_path, common_log_name)
        else:
            print("Execution canceled.")
    else:
        print("Execution canceled.")

    # If selected_clusters is empty or execution was canceled, process all files
    if not selected_clusters:
        process_all_files()
