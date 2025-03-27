import os
import time
import subprocess
import json

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

# UPSCALE
def perform_upscale():
    print("Upscaling")
    exit(0)

# DOWNSCALE
def perform_downscale():
    print("Downscaling")
    exit(0)

# CHECK UPSCALE / DOWNSCALE / TIMER
def check_load(load_avg, threshold_high, threshold_low, last_run_file):
    if load_avg > threshold_high:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        perform_upscale()
    elif load_avg < threshold_low:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        perform_downscale()

# MAIN
def main():
    # Config file
    config_file = 'threshold.conf'
    
    # Grab thresholds
    pool_type, thresholds = load_thresholds(config_file)

    last_run_file = '/tmp/last_run_time'

    current_time = int(time.time())


    # CHECK TIMER FILE
    if os.path.exists(last_run_file):
        with open(last_run_file, 'r') as f:
            last_run_time = int(f.read().strip())
    else:
        last_run_time = 0

    time_diff = current_time - last_run_time

    if time_diff < 300:
            print(f"Timer in progress, please wait {300 - time_diff} seconds")
            exit(0)

    # Greab load
    load_1min, load_5min, load_15min = get_load_averages()

    print(f"1-minute Load average: {load_1min}")
    print(f"5-minute Load average: {load_5min}")
    print(f"15-minute Load average: {load_15min}")
    print(f"Using pool type: {pool_type}")

    check_load(load_1min, thresholds['THRESHOLD_HIGH_1MIN'], thresholds['THRESHOLD_LOW_1MIN'], last_run_file)
    check_load(load_5min, thresholds['THRESHOLD_HIGH_5MIN'], thresholds['THRESHOLD_LOW_5MIN'], last_run_file)
    check_load(load_15min, thresholds['THRESHOLD_HIGH_15MIN'], thresholds['THRESHOLD_LOW_15MIN'], last_run_file)

if __name__ == "__main__":
    main()