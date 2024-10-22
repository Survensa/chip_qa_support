import os
import subprocess
import yaml
import argparse
import re
import time
import traceback
from datetime import datetime
from dataclasses import fields
from cluster_data import Cluster
from colorama import Fore, Style, init

init(autoreset=True)

clusters = fields(Cluster)
cluster_name = [field.name for field in clusters]

# Parse command-line arguments
parser = argparse.ArgumentParser(description="cluster name")
parser.add_argument(
    "-c",
    "--cluster",
    nargs="+",
    help="name of the cluster",
    choices=cluster_name,
    default=False,
)
args = parser.parse_args()

# Load configuration from YAML file
config_path = os.path.join(os.path.expanduser("~"), "chip_qa_support", "config.yaml")
with open(config_path, "r") as config_file:
    yaml_info = yaml.safe_load(config_file)
    build = yaml_info.get("chip_tool_directory")

# Folder Path
path = "../commands"

# Change the directory
os.chdir(path)


def remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def extarct_response(logs_of_steps):
    list_of_response = []
    for logs in logs_of_steps:
        read = False
        status = []
        for log in logs:
            if "Data = " in log :
                start_index = logs.index(log)
                read = True
           
            if "status = " in log:
                status.append(log)
        
        if read:
            end_pos = [pos for pos, char in enumerate(logs) if '},' in char]
            list_of_data = logs[start_index:end_pos[-2]]
            response = ' '.join(list_of_data)
            list_of_response.append(response.replace(" ",""))
        elif status:
            response = ' '.join(status)
            list_of_response.append(response.replace(" ",""))

    return list_of_response

def get_list_of_logs(output_file):
    logs_of_steps =[]
    temp_log =[]
    capture_log = False
    prefix = re.compile(r'\[.*?\]')
    with open(output_file, "r") as log_file:
        for line in log_file:
            if line.startswith('Command:'):
                if temp_log:
                    logs_of_steps.append(temp_log)
                    temp_log =[]
                capture_log = True
                continue

            if capture_log:
                if not line.startswith('Command:') and not line.startswith('#'):
                    clean_log = prefix.sub('',line).strip()
                    if clean_log:
                        temp_log.append(clean_log)

        if temp_log:
            logs_of_steps.append(temp_log)
        print(logs_of_steps)
    
    return extarct_response(logs_of_steps)

def check_logs(logs, output_file):
    list_of_response = get_list_of_logs(output_file)
    if logs == list_of_response:
        return True
    
    else:
        return False

def run_command_from_yaml(yaml_file_path):
    with open(yaml_file_path, "r") as yaml_file:
        yaml_input = yaml.safe_load(yaml_file)

    for testcase_data in yaml_input:
        testcase_name = testcase_data["testcase"]
        commands = testcase_data.get("commands", [])
        logs =[]
        commands_list = testcase_data.get("commands", [])
        
        if not commands_list:
            continue

        for step in commands_list:
            log = re.sub(r'[\n\t\r]', '', step["logs"])
            logs.append(log.replace(" ",""))

        file_path = os.path.join(os.path.expanduser("~"), build)
        save_path = os.path.join(
            os.path.expanduser("~"), "chip_qa_support", "logs", "execution_logs"
        )
        os.makedirs(save_path, exist_ok=True)
        os.chdir(file_path)
        date = datetime.now().strftime("%m_%Y_%d_(%I_%M_%S_%p)")

        log_filename = f"{testcase_name.replace(' ', '_')}-{date}.txt"
        log_file_path = os.path.join(save_path, log_filename)

        with open(log_file_path, "a") as cluster_textfile:
            cluster_textfile.write(f"Test Case: {testcase_name}\n\n")

        for command_data in commands:
            command = command_data["command"]
            print(f"{Fore.BLUE}EXT:CMD : {command}{Style.RESET_ALL}")
            with open(log_file_path, "a") as cluster_textfile:
                cluster_textfile.write(
                    f"Command: {remove_ansi_escape_codes(command)}\n"
                )
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            with open(log_file_path, "a") as cluster_textfile:
                cluster_textfile.write(remove_ansi_escape_codes(stdout))
                cluster_textfile.write(remove_ansi_escape_codes(stderr))

        # Process the specific log file immediately after running the command
        output_directory = os.path.join(
            os.path.expanduser("~"), "chip_qa_support", "logs", "validation_logs"
        )
        process_log_file(log_file_path, output_directory)
        output_file = os.path.join(output_directory, log_filename)
        print(f"{Fore.GREEN}EXT:CMP : {testcase_name}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}EXT:LOG : {log_filename}{Style.RESET_ALL}")
        check = check_logs(logs, output_file)
        if check:
            print(f"{Fore.GREEN}EXT:RESULT : {testcase_name} is PASS {Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}EXT:RESULT :  {testcase_name} is FAIL {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}EXT:COS : {'*' * 64}{Style.RESET_ALL}")
        



# Function to get the current epoch time
def get_epoch_time():
    return int(time.time())


# Function to process log files and save them
def process_log_file(input_file_path, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Construct the output file path using the input file name
    output_file_path = os.path.join(output_directory, os.path.basename(input_file_path))

    with open(input_file_path, "r") as input_file, open(
        output_file_path, "w"
    ) as output_file:
        start_epoch = get_epoch_time()
        output_file.write(f"# {start_epoch}\n")
        for line in input_file:
            line = line.rstrip()
            match1 = re.search(r"^Test Case:", line)
            match2 = re.search(r"(CHIP:DMG|CHIP:TOO|\[DMG\]|\[TOO\])(.*)", line)
            match3 = re.search(r"^Command:", line)
            if match1:
                output_file.write("\n" + line + "\n")
            if match2:
                chip_text = match2.group(1).rstrip()
                trailing_text = match2.group(2).rstrip()
                output_line = f"{chip_text} {trailing_text}"
                output_file.write(output_line + "\n")
            if match3:
                output_file.write("\n" + line + "\n\n")
        end_epoch = get_epoch_time()
        output_file.write(f"\n# {end_epoch}")


if __name__ == "__main__":
    selected_clusters = args.cluster

    build_confirmation = (
        input(
            f"\n{Fore.MAGENTA}EXT:ASK : Confirm the Chip-Tool Build Path: {build} (Y/Yes to confirm):{Style.RESET_ALL} "
        )
        .strip()
        .lower()
    )
    output_directory = os.path.join(
        os.path.expanduser("~"), "chip_qa_support", "logs", "validation_logs"
    )

    if build_confirmation in ["y", "yes"]:
        if selected_clusters:
            None
        else:
            selected_clusters = []
            for clus in cluster_name:
                e = yaml_info[clus]
                if e in ["Y", "Yes"]:
                    selected_clusters.append(clus)
        if not selected_clusters:
            clusters_confirmation = (
                input(
                    f"\n{Fore.MAGENTA}EXT:ASK : Proceed with all the clusters for execution (Y/Yes to proceed):{Style.RESET_ALL} "
                )
                .strip()
                .lower()
            )
            print(f"\n{Fore.YELLOW}EXT:COS : {'*' * 64}{Style.RESET_ALL}")
        else:
            clusters_confirmation = (
                input(
                    f"\n{Fore.MAGENTA}EXT:ASK : Proceed with selected Clusters {selected_clusters} for execution (Y/Yes to proceed):{Style.RESET_ALL} "
                )
                .strip()
                .lower()
            )
            print(f"\n{Fore.YELLOW}EXT:COS : {'*' * 64}{Style.RESET_ALL}")
        if clusters_confirmation in ["y", "yes"]:
            if selected_clusters:
                for cluster_name in selected_clusters:
                    file = vars(Cluster)[cluster_name]
                    file_path = os.path.join(
                        os.path.expanduser("~"), "chip_qa_support", "commands", file
                    )
                    if file.endswith(".yaml"):
                        print(
                            f"{Fore.CYAN}EXT:STR : {cluster_name} INITIATED{Style.RESET_ALL}"
                        )
                        try:
                            run_command_from_yaml(file_path)
                            print(
                                f"{Fore.CYAN}EXT:STP : {cluster_name} COMPLETED{Style.RESET_ALL}"
                            )
                        except Exception as e:
                            traceback.print_exc()
                            print(
                                f"{Fore.RED}EXT:ERR : {cluster_name}: {str(e)}{Style.RESET_ALL}"
                            )
                    print(
                        f"\n{Fore.YELLOW}EXT:SUS : Execution completed and Logged in {output_directory}{Style.RESET_ALL}\n"
                    )
            else:
                print(
                    f"\n{Fore.YELLOW}EXT:CNL : No cluster selected for execution.{Style.RESET_ALL}\n"
                )
        else:
            print(
                f"\n{Fore.YELLOW}EXT:CNL : Execution Canceled With The User Input: {clusters_confirmation}{Style.RESET_ALL}\n"
            )
    else:
        print(
            f"\nEXT:CNL : Execution Canceled With The User Input: {build_confirmation}\n"
        )
