import os
import time
import subprocess
import json

ACTION_LOG_FILE = 'action_log2.txt'
timer = 0

# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")


# Load JSON
def load_thresholds(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file) 
            
            pool_type = config.get('pool_type')
            
            if pool_type in config:
                thresholds = config[pool_type]  # THRESHOLDS
                return pool_type, thresholds
            else:
                print(f"Error: Pool type '{pool_type}' not found in configuration.")
                exit(1)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        exit(1)

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