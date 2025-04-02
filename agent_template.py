import subprocess
import json
import time

CONFIG_FILE_PATH = "config.json"
ACTION_LOG_FILE = "logs"
DATA_FILE = "data"

# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")

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

def get_data():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            data = json.load(file) 
        return data
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE_PATH}' not found.")
        exit(1)

def print_data(config_data, averages):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    with open(DATA_FILE, 'a') as data_file:
        data_file.write(f"{timestamp} - {config_data['pool']} - {config_data['id']} - {averages[0]}, {averages[1]}, {averages[2]}")

def main():
    
    log_action("Agent Started\n")


    config_data = get_data()
    load_avg = get_load_averages()
    print_data(config_data, load_avg)

    # Update status after script execution
    log_action("Script Terminated\n")


if __name__ == "__main__":
    main()