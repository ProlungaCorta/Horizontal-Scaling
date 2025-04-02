import socket
import time
import subprocess
import json

ACTION_LOG_FILE = "logs"
CONFIG_FILE_PATH = "config.json"

# LOAD AVERAGES
def get_load_averages():
    try:
        uptime_output = subprocess.check_output("uptime", shell=True).decode('utf-8')
        load_averages = uptime_output.split("load average: ")[1].split(",")
        load_1min = float(load_averages[0].strip())
        load_5min = float(load_averages[1].strip())
        load_15min = float(load_averages[2].strip())
        return load_1min, load_5min, load_15min
    except Exception as e:
        print(f"Error fetching load averages: {e}")
        exit(1)


# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")


def get_data():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            data = json.load(file) 
        return data
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE_PATH}' not found.")
        exit(1)


def data_to_send():
    averages = get_load_averages()
    config_data = get_data()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    return f"{timestamp} - {config_data['pool']} - {config_data['id']} - {averages[0]}, {averages[1]}, {averages[2]}"


# Function to send data to the master script
def send_data_to_master(data, host='127.0.0.1', port=12345):
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the master script (server)
            client_socket.connect((host, port))
            
            # Send data
            client_socket.sendall(data.encode('utf-8'))
            print(f"Sent data to master: {data}")
        except Exception as e:
            print(f"Error connecting to master: {e}")

# Main logic for agent to periodically send data
if __name__ == "__main__":
    while True:
        # Send the data to the master script
        data = data_to_send()
        send_data_to_master(data)
        # Wait before sending data again (simulate periodic task)
        time.sleep(60)