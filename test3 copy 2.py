import os
import time
import subprocess
import json

# Log files
ACTION_LOG_FILE = 'action_log.txt'
timer = 0

####################################################################################################################################

# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")

####################################################################################################################################

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

####################################################################################################################################

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

####################################################################################################################################

# UPSCALE
def perform_upscale():
    log_action("Performing upscaling")
    print("Upscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Upscale done successfully")
    log_action(f"Script terminated in {(current_time - first_run_time):.3f} secondi\n")
    exit(0)

####################################################################################################################################

# DOWNSCALE
def perform_downscale():
    log_action("Performing downscaling")
    print("Downscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Downscale done successfully")
    log_action(f"Script terminated in {(current_time - first_run_time):.3f} secondi\n")
    exit(0)

####################################################################################################################################

# CHECK UPSCALE / DOWNSCALE / TIMER
def check_load(load_avg, threshold_high, threshold_low, last_run_file):
    if load_avg > threshold_high:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        log_action("The load average is higher then the tresholds, upscaling needed")
        perform_upscale()
    elif load_avg < threshold_low:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        log_action("The load average is below the tresholds, downscale needed")
        perform_downscale()
    else:
        log_action("The load average is within the tresholds, nothing to do")

####################################################################################################################################

# MAIN
def main():
    global first_run_time

    # Log script start
    first_run_time = float(f"{time.time():.3f}")
    log_action("Scaling_Check_Sevice Started")

    # Config file
    config_file = 'threshold.conf'
    
    # Grab thresholds
    pool_type, thresholds = load_thresholds(config_file)

    last_run_file = '/tmp/last_run_time'

    current_time = int(time.time())

    # CHECK TIMER FILE
    if os.path.exists(last_run_file):
        with open(last_run_file, 'r') as f:
            readed = f.read()
            if readed != '':
                last_run_time = int(readed)
            else:
                last_run_time = 0
    else:
        last_run_time = 0

    time_diff = current_time - last_run_time

    if time_diff < timer:
        log_action(f"Timer in progress, {timer - time_diff} seconds left")
        print(f"Timer in progress, please wait {timer - time_diff} seconds")
        log_action("Script terminated\n")
        exit(0)

    # Grab load
    load_1min, load_5min, load_15min = get_load_averages()
    log_action(f"Using pool type: {pool_type}\t ({load_1min}, {load_5min}, {load_15min})\n")
    '''
    log_action(f"1-minute Load average: {load_1min}")
    log_action(f"5-minute Load average: {load_5min}")
    log_action(f"15-minute Load average: {load_15min}")
    '''
    log_action(f"Checking 1-Minute load average:")
    check_load(load_1min, thresholds['THRESHOLD_HIGH_1MIN'], thresholds['THRESHOLD_LOW_1MIN'], last_run_file)
    log_action(f"Checking 5-Minute load average:")
    check_load(load_5min, thresholds['THRESHOLD_HIGH_5MIN'], thresholds['THRESHOLD_LOW_5MIN'], last_run_file)
    log_action(f"Checking 15-Minute load average:")
    check_load(load_15min, thresholds['THRESHOLD_HIGH_15MIN'], thresholds['THRESHOLD_LOW_15MIN'], last_run_file)

    # Update status after script execution
    log_action("Script Terminated\n")

####################################################################################################################################

if __name__ == "__main__":
    main()
