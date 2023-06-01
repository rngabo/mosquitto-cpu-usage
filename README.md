# MQTT CPU Monitor


This program demonstrates the usage of Mosquitto MQTT broker to send messages to multiple brokers while monitoring the CPU usage of the Mosquitto processes running in the background.

## Prerequisites

Before running the program, make sure you have the following:

- Python 3.x installed on your system
- Mosquitto MQTT broker installed

## Installation

1. Clone the repository to your local machine:

     git clone <repository_url>

2. Change to the project directory:

     cd MQTT_CPU_Monitor

3. Install the required Python packages:

    pip install -r requirements.txt

## Usage

 1. Open the cpu_mqtt.py file in a text editor.

 2. Modify the topics and ports variables according to your desired MQTT broker setup. These variables define the topics and ports for each broker.
     Run the two brokers first
     - mosquitto -c /etc/mosquitto/conf.d/broker1.conf
     - mosquitto -c /etc/mosquitto/conf.d/broker2.conf

 3. Make sure that the two brokers are running, run the program using the following command:

     python3 cpu_mqtt.py

4. The program will start sending messages to the MQTT brokers specified in the topics and ports variables. It will display a progress bar indicating the number of messages sent.

5. At the end of the message sending process, the program will calculate and display the CPU & Memory usage for each Mosquitto process running on the brokers and the overall CPU and memory usage.

## Notes

- Ensure that the Mosquitto brokers are running and configured properly before running this program.
- The program uses subprocesses to execute the mosquitto_pub commands for message sending. Make sure that the mosquitto_pub command is accessible from the command line.

## License

This project is licensed under the MIT License.
