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
    BOOL : str = "../commands/Boolean.yml"
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
    ACE : str = "../commands/Access_Control_Enforcement.txt"

clusters = fields(Cluster)
cluster_name = [field.name for field in clusters]

# Parse command-line arguments
parser = argparse.ArgumentParser(description='cluster name')
parser.add_argument('-c', '--cluster', nargs='+', help='name of the cluster', choices=cluster_name, default=False)
args = parser.parse_args()

# Load configuration from YAML file
config_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "config.yaml")
with open(config_path, 'r') as config_file:
    yaml_info = yaml.safe_load(config_file)
    build = yaml_info.get("chip_tool_directory")

# Define regular expressions
pattern1 = re.compile(r'(CHIP:DMG|CHIP:TOO)(.*)')
pattern2 = re.compile(r'^\./chip-tool')

# Folder Path
path = "../commands"

# Change the directory
os.chdir(path)

# Function to run chip commands in terminal
def run_command(commands, testcase):
    file_path = os.path.join(os.path.expanduser('~'), build)
    save_path = os.path.join(os.path.expanduser('~'), "chip_command_run", "logs", "execution_logs")
    os.chdir(file_path)
    date = datetime.now().strftime("%m_%Y_%d-%I:%M:%S_%p")
    while "" in commands:
        commands.remove("")
    for i in commands:
        log_filename = f"{testcase}-{date}.txt"
        log_file_path = os.path.join(save_path, log_filename)
        with open(log_file_path, 'a') as cluster_textfile:
            print(testcase, i)
            cluster_textfile.write('\n' + i + '\n' + '\n')
        subprocess.run(i, shell=True, text=True, stdout=open(log_file_path, "a+"))
        output_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "logs", "validation_logs")
        process_log_file(log_file_path, output_directory)
    print(f"\n---------------------{testcase} - Executed----------------------")
    print(f"\nExecution log saved as {log_filename}")
    print(f"Validation log processed for {testcase}")
    print(f"\n****************************************************************")

# Function to process log files and save them
def process_log_file(input_file_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file_path = os.path.join(output_directory, os.path.basename(input_file_path))
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

# Function to read YAML test data
def read_yaml_data(yaml_file_path):
    with open(yaml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data

# Modify the process_all_files function to read YAML data
def process_all_files(yaml_dir):
    for file in os.listdir(yaml_dir):
        if file.endswith(".yaml"):
            file_path = os.path.join(yaml_dir, file)
            yaml_data = read_yaml_data(file_path)
            for item in yaml_data:
                testcase = item["testcase"]
                commands = item["commands"]
                run_command(commands, testcase)

if __name__ == "__main__":
    selected_clusters = args.cluster

    build_confirmation = input(f"\nConfirm the Chip-Tool Build Path: {build} (Y/Yes to confirm): ").strip().lower()
    output_directory = os.path.join(os.path.expanduser('~'), "chip_command_run", "logs", "validation_logs")

    if build_confirmation in ['y', 'yes']:
        if selected_clusters:
            None
        else:
            selected_clusters = []
            for clus in cluster_name:
                e = yaml_info[clus]
                if e in ['Y', 'Yes']:
                    selected_clusters.append(clus)
        if not selected_clusters:
            clusters_confirmation = input(f"\nProceed with all the clusters for execution (Y/Yes to proceed): ").strip().lower()
            print(f"\n****************************************************************")
        else:
            clusters_confirmation = input(f"\nProceed with selected Clusters {selected_clusters} for execution (Y/Yes to proceed): ").strip().lower()
            print(f"\n****************************************************************")
        if clusters_confirmation in ['y', 'yes']:
            if selected_clusters:
                for cluster_name in selected_clusters:
                    yaml_dir = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands")
                    process_all_files(yaml_dir)
                    print(f"\nExecution completed... Logs are ready for validation in {output_directory}")
            else:
                yaml_dir = os.path.join(os.path.expanduser('~'), "chip_command_run", "commands")
                process_all_files(yaml_dir)
                print(f"\nExecution completed... Logs are ready for validation in {output_directory}")
        else:
            print(f"\nExecution Canceled With The User Input: {clusters_confirmation}")
    else:
        print(f"\nExecution Canceled With User The User Input: {build_confirmation}")
