import subprocess
import psutil
import time
from tqdm import tqdm
import threading

def send_messages_to_brokers(topics, ports, num_messages):
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
            "-m"
        ]
        commands.append(command)

    # Send the messages to each broker in a loop and count the messages
    messages_sent = 0
    progress_bar = tqdm(total=num_messages, desc="Sending Messages", unit="msg")

    for i in range(1, num_messages + 1):
        message = f"{i}: {'X' * 51200}\n"  # Generate a message with the number at the beginning and a new line

        # Execute mosquitto_pub commands for each broker in separate processes
        for command in commands:
            command_with_message = command + [message]
            subprocess.Popen(command_with_message)

        messages_sent += 1
        progress_bar.update()

    progress_bar.close()

def calculate_mosquitto_cpu_usage():
    cpu_sum = 0
    for proc in psutil.process_iter(attrs=['name', 'cmdline', 'cpu_percent']):
        if proc.info['name'] == 'mosquitto' and 'mosquitto' in proc.info['cmdline']:
            cpu_sum += proc.info['cpu_percent']
    return cpu_sum

if __name__ == "__main__":
    topics = ["test", "test"]  # Topics for both brokers
    ports = [1221, 1222]  # Ports for both brokers
    num_messages = 50000

    # Start sending messages to the brokers in a separate thread
    send_thread = threading.Thread(target=send_messages_to_brokers, args=(topics, ports, num_messages))
    send_thread.start()

    # Calculate the sum of the CPU usage for all mosquitto processes in the background
    cpu_sum = 0
    while send_thread.is_alive():
        cpu_sum = calculate_mosquitto_cpu_usage()
        time.sleep(1)  # Adjust the interval as needed

    # Wait for the message sending thread to complete
    send_thread.join()

    # Display the sum of the CPU usage for all mosquitto processes
    print(f"Sum of Mosquitto CPU Usage: {cpu_sum}%")
