import time
import os
import json

ACTION_LOG_FILE = 'action_log2.txt'
config_file = 'threshold2.conf'
input_file = "test.txt"
status_file_path = "_status"
timer = 0

####################################################################################################################################

# Write to the action log file
def log_action(message):
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")

####################################################################################################################################

# Create status file (generico perfavore)
def create_status_files(status_file, pool):
    if os.path.exists(status_file):
        return
    else:
        with open(status_file, 'w') as f:
            status_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} - Created current status file for the pool {pool}")
            lines = read_file_lines_to_list()
            for line in lines:
                data = parse_load_averages(line)
                if data[1] == pool:
                    status_file.write(f"{line}\n")

        '''
        l'obbiettivo sarebbe creare un file di status con una funzione generica che listi le macchine del pool,
        il file di status puo essere un json cosi da tenere un dizionario delle macchine 
        tenere nota del numero delle macchine in un pool così da non fare downscale con una macchina singola
        avere la possibilita di modificare in caso di upscale e downscale (forse 2 funzioni)
        piangere
        '''

####################################################################################################################################

# Load JSON
def load_thresholds():
    try:
        with open(config_file, 'r') as file:
            config = json.load(file) 
            global web_t, db_t, monit_t
            web_t = config["web"]
            db_t = config["db"]
            monit_t = config["monit"]
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
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

def read_file_lines_to_list(input_file):
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()  # Read all lines into a list
        return [line.strip() for line in lines]  # Strip trailing newlines and return the list
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")

####################################################################################################################################

# CHECK UPSCALE / DOWNSCALE / TIMER
def check_load():
    
    lines = read_file_lines_to_list()
    for line in lines:
        averages = parse_load_averages(line)
        if averages[0] == "web":
            log_action(f"Checking 1-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[2], web_t['THRESHOLD_LOW_1MIN'], web_t['THRESHOLD_HIGH_1MIN']):
                continue
            log_action(f"Checking 5-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[3], web_t['THRESHOLD_LOW_15MIN'], web_t['THRESHOLD_HIGH_15MIN']):
                continue
            log_action(f"Checking 15-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[4], web_t['THRESHOLD_LOW_5MIN'], web_t['THRESHOLD_HIGH_5MIN']):
                continue
        
        if averages[0] == "db":
            log_action(f"Checking 1-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[2], db_t['THRESHOLD_LOW_1MIN'], db_t['THRESHOLD_HIGH_1MIN']):
                continue
            log_action(f"Checking 5-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[3], db_t['THRESHOLD_LOW_15MIN'], db_t['THRESHOLD_HIGH_15MIN']):
                continue
            log_action(f"Checking 15-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[4], db_t['THRESHOLD_LOW_5MIN'], db_t['THRESHOLD_HIGH_5MIN']):
                continue
        
        if averages[0] == "monit":
            log_action(f"Checking 1-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[2], monit_t['THRESHOLD_LOW_1MIN'], monit_t['THRESHOLD_HIGH_1MIN']):
                continue
            log_action(f"Checking 5-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[3], monit_t['THRESHOLD_LOW_15MIN'], monit_t['THRESHOLD_HIGH_15MIN']):
                continue
            log_action(f"Checking 15-Minute load average of the machine {averages[1]}, from the pool {averages[0]}, {averages[2], averages[3], averages[4]}")
            if check_single_load(averages[4], monit_t['THRESHOLD_LOW_5MIN'], monit_t['THRESHOLD_HIGH_5MIN']):
                continue

####################################################################################################################################

def check_single_load(load_avg, threshold_low, threshold_high):
    if load_avg > threshold_high:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        log_action("The load average is higher then the tresholds, upscaling needed")
        perform_upscale()
        return True
    elif load_avg < threshold_low:
        with open(last_run_file, 'w') as f:
            f.write(str(int(time.time())))
        log_action("The load average is below the tresholds, downscale needed")
        perform_downscale()
        return True
    else:
        current_time = float(f"{time.time():.3f}")
        log_action("The load average is within the tresholds, nothing to do")
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
    global first_run_time
    global last_run_file

    #timer script starts
    last_run_file = '/tmp/last_run_time'
    # Log script start
    first_run_time = float(f"{time.time():.3f}")
    log_action("Scaling_Check_Sevice Started\n")
    
    # Grab thresholds
    load_thresholds()

    check_load()



#    # CHECK TIMER FILE
#    if os.path.exists(last_run_file):
#        with open(last_run_file, 'r') as f:
#            readed = f.read()
#            if readed != '':
#                last_run_time = int(readed)
#            else:
#                last_run_time = 0
#    else:
#        last_run_time = 0
#
#    time_diff = current_time - last_run_time
#
#    if time_diff < timer:
#        log_action(f"Timer in progress, {timer - time_diff} seconds left")
#        print(f"Timer in progress, please wait {timer - time_diff} seconds")
#        log_action("Script terminated\n")
#        exit(0)

    

    # Update status after script execution
    log_action("Script Terminated\n")


if __name__ == "__main__":
    main()
