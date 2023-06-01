import os
import subprocess

def get_pid(port):
    # Use netstat to find the PID of the process using the specified port
    netstat_cmd = ["netstat", "-nlp", "--inet"]
    output = subprocess.check_output(netstat_cmd).decode("utf-8").splitlines()
    for line in output:
        if f":{port}" in line:
            return line.split()[6].split("/")[0]
    return None

def kill_process(pid):
    # Kill the process with the specified PID
    kill_cmd = ["kill", str(pid)]
    subprocess.run(kill_cmd)

def restart_mosquitto():
    # Restart the Mosquitto service
    restart_cmd = ["systemctl", "restart", "mosquitto"]
    subprocess.run(restart_cmd)

# Check and kill processes running on port 1221
pid_1221 = get_pid(1221)
if pid_1221:
    print(f"Process running on port 1221 (PID {pid_1221}) found. Killing the process...")
    kill_process(pid_1221)
else:
    print("No process found running on port 1221.")

# Check and kill processes running on port 1222
pid_1222 = get_pid(1222)
if pid_1222:
    print(f"Process running on port 1222 (PID {pid_1222}) found. Killing the process...")
    kill_process(pid_1222)
else:
    print("No process found running on port 1222.")

# Restart Mosquitto
print("Restarting Mosquitto...")
restart_mosquitto()
print("Mosquitto restarted.")
