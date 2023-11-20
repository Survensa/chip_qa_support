import os
import subprocess
import yaml
import argparse
import re
from datetime import datetime
from dataclasses import fields
from cluster_data import Cluster

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
config_path = os.path.join(os.path.expanduser("~"), "chip_command_run", "config.yaml")
with open(config_path, "r") as config_file:
    yaml_info = yaml.safe_load(config_file)
    build = yaml_info.get("chip_tool_directory")

# Folder Path
path = "../commands"

# Change the directory
os.chdir(path)


# Function to run chip commands in terminal
def run_command_from_yaml(yaml_file_path):
    with open(yaml_file_path, "r") as yaml_file:
        yaml_input = yaml.safe_load(yaml_file)

    for testcase_data in yaml_input:
        testcase_name = testcase_data["testcase"]
        commands = testcase_data.get("commands", [])
        if not commands:
            continue

        file_path = os.path.join(os.path.expanduser("~"), build)
        save_path = os.path.join(
            os.path.expanduser("~"), "chip_command_run", "logs", "execution_logs"
        )
        os.chdir(file_path)
        date = datetime.now().strftime("%m_%Y_%d_(%I_%M_%S_%p)")

        log_filename = f"{testcase_name.replace(' ', '_')}-{date}.txt"
        log_file_path = os.path.join(save_path, log_filename)

        with open(log_file_path, "a") as cluster_textfile:
            cluster_textfile.write(f"Test Case: {testcase_name}\n\n")

        for command_data in commands:
            command = command_data["command"]
            print(f"EXT:CMD : {command}")
            with open(log_file_path, "a") as cluster_textfile:
                cluster_textfile.write(f"Command: {command}\n")
            subprocess.run(
                command, shell=True, text=True, stdout=open(log_file_path, "a+")
            )

        # Process the specific log file immediately after running the command
        output_directory = os.path.join(
            os.path.expanduser("~"), "chip_command_run", "logs", "validation_logs"
        )
        process_log_file(log_file_path, output_directory)
        print(f"EXT:CMP : {testcase_name} ")
        print(f"EXT:LOG : {log_filename}")
        print(
            "EXT:COS : ****************************************************************"
        )


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
        for line in input_file:
            line = line.strip()
            match1 = re.search(r"(CHIP:DMG|CHIP:TOO)(.*)", line)
            match2 = re.search(r"^Command:", line)
            if match1:
                chip_text = match1.group(1).strip()
                trailing_text = match1.group(2).strip()
                output_line = f"{chip_text} {trailing_text}"
                output_file.write(output_line + "\n")
            if match2:
                output_file.write("\n" + line + "\n\n")


if __name__ == "__main__":
    selected_clusters = args.cluster

    build_confirmation = (
        input(
            f"\nEXT:ASK : Confirm the Chip-Tool Build Path: {build} (Y/Yes to confirm): "
        )
        .strip()
        .lower()
    )
    output_directory = os.path.join(
        os.path.expanduser("~"), "chip_command_run", "logs", "validation_logs"
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
                    "\nEXT:ASK : Proceed with all the clusters for execution (Y/Yes to proceed): "
                )
                .strip()
                .lower()
            )
            print(
                "\nEXT:COS : ****************************************************************"
            )
        else:
            clusters_confirmation = (
                input(
                    f"\nEXT:ASK : Proceed with selected Clusters {selected_clusters} for execution (Y/Yes to proceed): "
                )
                .strip()
                .lower()
            )
            print(
                "\nEXT:COS : ****************************************************************"
            )
        if clusters_confirmation in ["y", "yes"]:
            if selected_clusters:
                for cluster_name in selected_clusters:
                    file = vars(Cluster)[cluster_name]
                    file_path = os.path.join(
                        os.path.expanduser("~"), "chip_command_run", "commands", file
                    )
                    if file.endswith(".yaml"):
                        print(f"EXT:STR : {cluster_name} INITIATED")
                        try:
                            run_command_from_yaml(file_path)
                            print(f"EXT:STP : {cluster_name} COMPLETED")
                        except Exception as e:
                            print(f"EXT:ERR : {cluster_name}: {str(e)}")
                    print(
                        f"\nEXT:SUS : Execution completed and Logged in {output_directory}"
                    )
            else:
                print("\nEXT:CNL : No cluster selected for execution.")
        else:
            print(
                f"\nEXT:CNL : Execution Canceled With The User Input: {clusters_confirmation}"
            )
    else:
        print(
            f"\nEXT:CNL : Execution Canceled With The User Input: {build_confirmation}"
        )
