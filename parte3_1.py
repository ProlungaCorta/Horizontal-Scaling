import time
import os
import json

ACTION_LOG_FILE = 'action_log.txt'
CONFIG_FILE_PATH = 'threshold2.conf'
INPUT_FILE_PATH = "data.txt"
STATUS_FILE_PATH = 'status.json'
first_run_time = float(f"{time.time():.3f}")

####################################################################################################################################

# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")

####################################################################################################################################

# grab data from the agents to the local data file
def pull_data():
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)
    


####################################################################################################################################

def check_status_timer(pool_name):
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)
    
    timer = status[pool_name]["timer_timestamp_in_epoch"]
    if (int(time.time()) - timer) <= 300:
        return False
    else:
        return True
    
####################################################################################################################################

def check_machine_number(pool_name):
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)
    return status[pool_name]["machine_count"]
    

####################################################################################################################################

def update_status(pool_name, machine_id, action, loads):
    # Load the current status from the file
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)

    # Get the current time
    current_time = int(time.time())
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    
    # Update the last action timestamp and performed status
    status[pool_name]["last_action_timestamp"] = timestamp
    status[pool_name]["last_action_performed"] = action

    # Update machine data for the specified machine
    status[pool_name]["machines"][machine_id]["last_load_averages"] = loads

    # If the action is 'outscale', add a new machine to the pool
    if action == "outscale":
        status[pool_name]["timer_timestamp_in_epoch"] = current_time
        new_machine_id = str(int(status[pool_name]["machine_count"]) + 1)
        new_machine_data = {
            "creation_date": timestamp,
            "last_load_averages": loads
        }

        # Add the new machine to the pool
        status[pool_name]["machines"][new_machine_id] = new_machine_data
        status[pool_name]["machine_count"] += 1
    elif action == "inscale":
        status[pool_name]["timer_timestamp_in_epoch"] = current_time
        # Remove the last machine based on the highest machine_id
        last_machine_id = str(status[pool_name]["machine_count"])  # Get the ID of the last machine
        if last_machine_id in status[pool_name]["machines"]:
            # Remove the last machine from the pool
            del status[pool_name]["machines"][last_machine_id]
            status[pool_name]["machine_count"] -= 1

    # Save the updated status back to the file
    with open(STATUS_FILE_PATH, 'w') as file:
        json.dump(status, file, indent=4)

    log_action("Updated status file")


####################################################################################################################################

#CREATE INITIAL STATUS
def create_status_file_from_config():

    # Load configuration from the config file
    with open(CONFIG_FILE_PATH, 'r') as f:
        config_data = json.load(f)

    # Get the number of pools from the config
    # Prepare the base data structure for the status file
    pools_data = {}

    # Get the pool names from the config
    pool_names = list(config_data.keys())

    # Create each pool with a single machine
    for i in range(len(pool_names)):
        pool_name = pool_names[i]
        
        # Set default values for machine in this pool
        current_time = int(time.time())
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

        pools_data[pool_name] = {
            "first_creation_timestamp": formatted_time,
            "machine_count": 1,  # Initially one machine in each pool
            "last_action_timestamp": formatted_time,
            "timer_timestamp_in_epoch": current_time,
            "last_action_performed": "no_data",
            "machines" : {
                "1": {
                    "creation_date": "2025-03-31 08:24:49",
                    "last_load_averages": [0.0, 0.0, 0.0]
                }
            }
        }

    # Write the data to the status file
    with open(STATUS_FILE_PATH, 'w') as f:
        json.dump(pools_data, f, indent=4)

    log_action("Created default status file")


####################################################################################################################################

# Load JSON
def load_thresholds():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            thresholds = json.load(file) 
        return thresholds
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE_PATH}' not found.")
        exit(1)

####################################################################################################################################

def parse_load_averages(line):
    try:
        # Split the line into parts based on the ' - ' separator
        parts = line.strip().split(' - ')

        # Extract the pool, machine ID, and load averages
        timestamp = parts[0]
        pool = parts[1]
        machine_id = parts[2]
        load_averages = parts[3].split(', ')

        to_return = [pool, machine_id, float(load_averages[0]), float(load_averages[1]), float(load_averages[2]), timestamp]
        return to_return
    
    except Exception as e:
        print(f"Error parsing line: {e}")
        return None

####################################################################################################################################

def read_file_lines_to_list():
    try:
        with open(INPUT_FILE_PATH, 'r') as file:
            lines = file.readlines()  # Read all lines into a list
        return [line.strip() for line in lines]  # Strip trailing newlines and return the list
    except FileNotFoundError:
        print(f"Error: The file {INPUT_FILE_PATH} was not found.")

####################################################################################################################################

# CHECK UPSCALE / DOWNSCALE / TIMER
def check_load(thresholds):
    
    lines = read_file_lines_to_list()

    for line in lines:
        line_data = parse_load_averages(line)
        log_action(f"Checking 1-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
        if check_single_load(line_data[2], thresholds[line_data[0]]['THRESHOLD_LOW_1MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_1MIN'], line_data):
            continue
        log_action(f"Checking 5-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
        if check_single_load(line_data[3], thresholds[line_data[0]]['THRESHOLD_LOW_15MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_15MIN'], line_data):
            continue
        log_action(f"Checking 15-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
        if check_single_load(line_data[4], thresholds[line_data[0]]['THRESHOLD_LOW_5MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_5MIN'], line_data):
            continue

####################################################################################################################################

def check_single_load(load_avg, threshold_low, threshold_high, line_data):
    if load_avg > threshold_high:
        log_action("The load average is higher then the tresholds, upscaling needed")
        if check_status_timer(line_data[0]):
            update_status(line_data[0], line_data[1], "outscale", [line_data[2], line_data[3], line_data[4]])
            perform_upscale()
            return True
        elif check_machine_number(line_data[0]) >= 10:
            log_action("Max number of machines reached, outscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - first_run_time):.3f} secondi\n")
            return False
        else:
            log_action("Timer in progress, outscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - first_run_time):.3f} secondi\n")
            return False
        
    elif load_avg < threshold_low:
        log_action("The load average is below the tresholds, downscale needed")
        if check_status_timer(line_data[0]):
            update_status(line_data[0], line_data[1], "inscale", [line_data[2], line_data[3], line_data[4]])
            perform_downscale()
            return True
        elif check_machine_number(line_data[0]) <= 1:
            log_action("There is only 1 machine in the pool, outscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - first_run_time):.3f} secondi\n")
            return False
        else:
            log_action("Timer in progress inscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - first_run_time):.3f} secondi\n")
            return False
    else:
        log_action("The load average is within the tresholds, nothing to do")
        update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
        current_time = float(f"{time.time():.3f}")
        log_action(f"Check terminated in {(current_time - first_run_time):.3f} secondi\n")
        return False

####################################################################################################################################

# UPSCALE
def perform_upscale():
    log_action("Performing upscale")
    print("Upscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Upscale done successfully")
    log_action(f"Upscale terminated in {(current_time - first_run_time):.3f} secondi\n")

####################################################################################################################################

# DOWNSCALE
def perform_downscale():
    log_action("Performing downscale")
    print("Downscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Downscale done successfully")
    log_action(f"Downscale terminated in {(current_time - first_run_time):.3f} secondi\n")

####################################################################################################################################


def main():
    
    log_action("Scaling_Check_Sevice Started\n")

    if not os.path.exists(STATUS_FILE_PATH):
        create_status_file_from_config()

    # Grab thresholds
    thresholds = load_thresholds()

    check_load(thresholds)

    # Update status after script execution
    log_action("Script Terminated\n")


if __name__ == "__main__":
    main()
