import subprocess
import psutil
import time
from tqdm import tqdm
import threading

def send_messages_to_brokers(topics, ports, num_messages):
    # Construct the mosquitto_pub commands for each broker
    commands = [
        [
            "mosquitto_pub",
            "-h",
            "127.0.0.1",
            "-p",
            str(port),
            "-t",
            topic,
            "-m"
        ]
        for topic, port in zip(topics, ports)
    ]

    # Send the messages to each broker in a loop and count the messages
    messages_sent = 0
    progress_bar = tqdm(total=num_messages, desc="Sending Messages", unit="msg")

    for i in range(1, num_messages + 1):
        message = f"{i}: {'X' * 10240}\n"  # Generate a message with the number at the beginning and a new line

        # Execute mosquitto_pub commands for each broker in separate processes
        for command in commands:
            command_with_message = command + [message]
            subprocess.Popen(command_with_message)

        messages_sent += 1
        progress_bar.update()

    progress_bar.close()

def get_mosquitto_pids():
    mosquitto_pids = []

    for proc in psutil.process_iter(['name', 'pid']):
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

def get_memory_usage(pid):
    process = psutil.Process(pid)
    return process.memory_percent()

def get_cpu_frequency():
    return psutil.cpu_freq().current  # Get the current CPU frequency in MHz

if __name__ == "__main__":
    topics = ["test", "test"]  # Topics for both brokers
    ports = [1221, 1222]  # Ports for both brokers
    num_messages = 50000

    # Start sending messages to the brokers in a separate thread
    send_thread = threading.Thread(target=send_messages_to_brokers, args=(topics, ports, num_messages))
    send_thread.start()

    mosquitto_pids = get_mosquitto_pids()
    cpu_usage_results = {}
    memory_usage_results = {}

    while send_thread.is_alive():
        for pid in mosquitto_pids:
            cpu_usage = get_cpu_usage(pid, duration=5)  # Track CPU usage over a 5-second duration
            memory_usage = get_memory_usage(pid)  # Get memory usage

            if pid in cpu_usage_results:
                cpu_usage_results[pid].extend(cpu_usage)
            else:
                cpu_usage_results[pid] = cpu_usage

            if pid in memory_usage_results:
                memory_usage_results[pid].append(memory_usage)
            else:
                memory_usage_results[pid] = [memory_usage]

        time.sleep(1)  # Adjust the interval as needed

    # Wait for the message sending thread to complete
    send_thread.join()

    # Calculate the max CPU usage and memory usage for each process
    max_cpu_usage_results = {
        pid: max(cpu_usage_list)
        for pid, cpu_usage_list in cpu_usage_results.items()
        if cpu_usage_list
    }

    max_memory_usage_results = {
        pid: max(memory_usage_list)
        for pid, memory_usage_list in memory_usage_results.items()
        if memory_usage_list
    }

    print("Max CPU Usage:")
    for pid, max_cpu_usage in max_cpu_usage_results.items():
        print(f"PID: {pid}, CPU Usage: {max_cpu_usage:.2f}%")

    print("Max Memory Usage:")
    for pid, max_memory_usage in max_memory_usage_results.items():
        print(f"PID: {pid}, Memory Usage: {max_memory_usage:.2f}%")

    # Get the current CPU frequency
    cpu_frequency = get_cpu_frequency()
    print(f"Current CPU Frequency: {cpu_frequency} MHz")

    # Calculate the total CPU usage for both brokers
    total_cpu_usage = sum(max_cpu_usage_results.values())
    print(f"Total CPU Usage for both brokers: {total_cpu_usage:.2f}%")

    # Calculate the total memory usage for both brokers
    total_memory_usage = sum(max_memory_usage_results.values())
    print(f"Total Memory Usage for both brokers: {total_memory_usage:.2f}%")
