import subprocess
import psutil
import time
from tqdm import tqdm
import threading

def send_messages_to_brokers(topics, ports, num_messages, username, password, qos):
    # Construct the mosquitto_pub commands for each broker
    commands = []
    for i in range(len(topics)):
        command = [
            "mosquitto_pub",
            "-h",
            "127.0.0.1",
            "-p",
            str(ports[i]),
            "-t",
            topics[i],
            "-m",
            "X" * 10240,
            "-u",
            username,
            "-P",
            password,
            "-q",
            str(qos)
        ]
        commands.append(command)

    # Send the messages to each broker in a loop and count the messages
    messages_sent = 0
    progress_bar = tqdm(total=num_messages, desc="Sending Messages", unit="msg")

    for i in range(1, num_messages + 1):
        # Execute mosquitto_pub commands for each broker in separate processes
        for command in commands:
            subprocess.Popen(command)

        messages_sent += 1
        progress_bar.update()

    progress_bar.close()

def get_mosquitto_pids():
    mosquitto_pids = []

    for proc in psutil.process_iter(attrs=['name', 'pid']):
        if proc.info['name'] == 'mosquitto':
            mosquitto_pids.append(proc.info['pid'])

    return mosquitto_pids

def get_cpu_usage(pid, duration):
    process = psutil.Process(pid)
    cpu_percentages = []
    start_time = time.time()

    while time.time() - start_time < duration:
        cpu_percent = process.cpu_percent(interval=0.1)  # Check CPU usage every 0.1 seconds
        cpu_percentages.append(cpu_percent)

    return cpu_percentages

if __name__ == "__main__":
    topics = ["test", "test"]  # Topics for both brokers
    ports = [1221, 1222]  # Ports for both brokers
    num_messages = 50000
    username = "mosq-user1"
    password = "Aa000000"
    qos = 2 # 0 message may be received or not, 1 duplicated may occur, 2 exactly once

    # Start sending messages to the brokers in a separate thread
    send_thread = threading.Thread(target=send_messages_to_brokers, args=(topics, ports, num_messages, username, password, qos))
    send_thread.start()

    mosquitto_pids = get_mosquitto_pids()
    cpu_usage_results = {}

    while send_thread.is_alive():
        for pid in mosquitto_pids:
            cpu_usage = get_cpu_usage(pid, duration=5)  # Track CPU usage over a 5-second duration

            if pid in cpu_usage_results:
                cpu_usage_results[pid].extend(cpu_usage)
            else:
                cpu_usage_results[pid] = cpu_usage

        time.sleep(1)  # Adjust the interval as needed

    # Wait for the message sending thread to complete
    send_thread.join()

    # Calculate the max CPU usage for each process
    max_cpu_usage_results = {}

    for pid, cpu_usage_list in cpu_usage_results.items():
        if cpu_usage_list:
            max_cpu_usage = max(cpu_usage_list)
            max_cpu_usage_results[pid] = max_cpu_usage

    print("Max CPU Usage:")
    for pid, max_cpu_usage in max_cpu_usage_results.items():
        print(f"PID: {pid}, Max CPU Usage: {max_cpu_usage:.2f}%")
