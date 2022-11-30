import json
import subprocess

# Build inputs
with open('/home/ubuntu/CHIP_Automation/SDK_Automation/build_config.json', 'r') as file:
    json_info = file.read()
    user_input = json.loads(json_info)
    folder = user_input["folder"]
    build = user_input["Connectedhomeip"]
    branch = user_input["branch"]
    commit = user_input["commit"]
    all_clusters_app = user_input["all_clusters_app"]
    all_clusters_minimal_app = user_input["all_clusters_minimal_app"]
    bridge_app = user_input["bridge_app"]
    lock_app = user_input["lock_app"]
    tv_app = user_input["tv_app"]
    lighting_app = user_input["lighting_app"]
    thermostat = user_input["thermostat"]
    tv_casting_app = user_input["tv_casting_app"]
    ota_provider_app = user_input["ota_provider_app"]
    ota_requestor_app = user_input["ota_requestor_app"]
    chip_tool = user_input["chip_tool"]

Boot1: str = "./scripts/bootstrap.sh"
Boot2: str = "./scripts/activate.sh"

# Building Apps
if build == "Y":
    print("\nClone connectedhomeip\n")
    subprocess.run("cd ~/" + folder + "&& git clone  https://github.com/project-chip/connectedhomeip.git", shell=True)

subprocess.run("cd ~/" + folder + "/connectedhomeip && git checkout " + branch, shell=True)
print("\nYour Branch is in :-" + branch)

print("\nGit pull\n")
subprocess.run("cd ~/" + folder + "/connectedhomeip && git pull", shell=True)

if commit != "N":
    subprocess.run("cd ~/" + folder + "/connectedhomeip && git switch -C " + commit, shell=True)

subprocess.run("cd ~/" + folder + "/connectedhomeip/scripts/ && chmod +x bootstrap.sh", shell=True)

print("\nSource bootstrap\n")
subprocess.run("cd ~/" + folder + "/connectedhomeip && " + Boot1, shell=True)

print("\nActivate bootstrap\n")
subprocess.run("cd ~/" + folder + "/connectedhomeip && " + Boot2, shell=True)

if all_clusters_app == "Y":
    print("\nBuilding all_clusters_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/all-clusters-app/linux/      "
                           "examples/all-clusters-app/linux/out/all-clusters-app   chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/all-clusters-app/linux/out/all-clusters-app"
                           "/chip-all-clusters-app all-cluster-app",
        shell=True)

if all_clusters_minimal_app == "Y":
    print("\nBuilding all_clusters_minimal_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/all-clusters-minimal-app/linux/      "
                           "examples/all-clusters-minimal-app/linux/out/all-clusters-minimal-app   "
                           "chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/all-clusters-minimal-app/linux/out/all"
                           "-clusters-minimal-app/chip-all-clusters-minimal-app all-clusters-minimal-app",
        shell=True)

if bridge_app == "Y":
    print("\nBuilding bridge_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      examples/bridge-app/linux/  "
                           "    examples/bridge-app/linux/out/bridge-app chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/bridge-app/linux/out/bridge-app/chip-bridge"
                           "-app bridge-app",
        shell=True)

if tv_app == "Y":
    print("\nBuilding tv_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      examples/tv-app/linux/      "
                           "examples/tv-app/linux/out/tv-app chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/tv-app/linux/out/tv-app/chip-tv-app tv-app",
        shell=True)

if tv_casting_app == "Y":
    print("\nBuilding tv_casting_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/tv-casting-app/linux/      examples/tv-casting-app/linux/out/tv-casting-app "
                           "chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/tv-casting-app/linux/out/tv-casting-app/chip"
                           "-tv-casting-app tv-casting-app",
        shell=True)

if lighting_app == "Y":
    print("\nBuilding lighting_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/lighting-app/linux/      examples/lighting-app/linux/out/lighting-app "
                           "chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/lighting-app/linux/out/lighting-app/chip"
                           "-lighting-app lighting-app",
        shell=True)

if thermostat == "Y":
    print("\nBuilding thermostat\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      examples/thermostat/linux/  "
                           "    examples/thermostat/linux/out/thermostat chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/thermostat/linux/out/thermostat/thermostat-app "
                           "thermostat-app",
        shell=True)

if ota_provider_app == "Y":
    print("\nBuilding ota_provider_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/ota-provider-app/linux      examples/ota-provider-app/linux/out/host "
                           "chip_config_network_layer_ble=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/ota-requestor-app/linux/out/host/chip-ota"
                           "-requestor-app ota-requestor-app",
        shell=True)

if ota_requestor_app == "Y":
    print("\nBuilding ota_requestor_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      "
                           "examples/ota-requestor-app/linux      examples/ota-requestor-app/linux/out/host "
                           "chip_config_network_layer_ble=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/ota-provider-app/linux/out/host/chip-ota"
                           "-provider-app ota-provider-app",
        shell=True)
if lock_app == "Y":
    print("\nBuilding lock_app\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && scripts/examples/gn_build_example.sh      examples/lock-app/linux/    "
                           "  examples/lock-app/linux/out/lock-app   chip_inet_config_enable_ipv4=false",
        shell=True)
    subprocess.run(
        "cd ~/" + folder + "/apps && ln -s ../connectedhomeip/examples/lock-app/linux/out/lock-app/chip-lock-app "
                           "lock-app",
        shell=True)
if chip_tool == "Y":
    print("\nBuilding chip_tool\n")
    subprocess.run(
        "cd ~/" + folder + "/connectedhomeip && gn gen out/debug --args='chip_mdns=\"platform\" "
                           "chip_inet_config_enable_ipv4=false'",
        shell=True)
    subprocess.run("cd ~/" + folder + "/connectedhomeip && ninja -C out/debug", shell=True)
    subprocess.run("cd ~/" + folder + "/apps && ln -s ../connectedhomeip/out/debug/chip-tool chip-tool", shell=True)
    subprocess.run("cd ~/" + folder + "/apps && ln -s ../connectedhomeip/out/debug/chip-shell chip-shell", shell=True)
    subprocess.run("cd ~/" + folder + '/apps && ln -s ../connectedhomeip/out/debug/chip-cert chip-cert', shell=True)
