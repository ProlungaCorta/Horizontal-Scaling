import time
import os
import json
import asyncio


ACTION_LOG_FILE = 'action.log' #path to the log file 
CONFIG_FILE_PATH = 'threshold.conf' #path to the configuration file with the thresholds
STATUS_FILE_PATH = 'status.json' #path to the status file, or where it should be created


####################################################################################################################################

# LOGGING
def log_action(message):  #open the log file and append the message with the current timestamp
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")


####################################################################################################################################

#TIMER
def check_status_timer(pool_name):   
#open the status file and read the timer timestamp (the last time an inscale or outscale was performed in epoch) and return true if 300 seconds passed and false if not 

    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)
    
    timer = status[pool_name]["timer_timestamp_in_epoch"]

    if (int(time.time()) - timer) <= 300:
        return False
    else:
        return True
    
####################################################################################################################################

#MACHINE COUNT PER POOL
def check_machine_number(pool_name):  
    #open the status file and return the number of machines in a pool, so that we can remain between 1 and 10 machines
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)
    return status[pool_name]["machine_count"]
    

####################################################################################################################################

#UPADTE STATUS
def update_status(pool_name, machine_id, action, loads): 
    #function to update the status file with the last action performed and last data


    #Load the current status from the file
    with open(STATUS_FILE_PATH, 'r') as file:
        status = json.load(file)

    # Get the current time
    current_time = int(time.time())
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    
    # Update what the last action was and when it was done
    status[pool_name]["last_action_timestamp"] = timestamp
    status[pool_name]["last_action_performed"] = action

    # Update the machine loads data with the current ones used for the check
    status[pool_name]["machines"][machine_id]["last_load_averages"] = loads

    # If the action is 'outscale', add a new machine to the pool
    if action == "outscale":
        status[pool_name]["timer_timestamp_in_epoch"] = current_time
        new_machine_id = str(int(status[pool_name]["machine_count"]) + 1)
        new_machine_data = {
            "creation_date": timestamp,
            "last_load_averages": loads
        }
        status[pool_name]["machines"][new_machine_id] = new_machine_data
        status[pool_name]["machine_count"] += 1

    # If the action is 'inscale', remove the last machine from the pool    
    elif action == "inscale":
        status[pool_name]["timer_timestamp_in_epoch"] = current_time
        last_machine_id = str(status[pool_name]["machine_count"])
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
    #create a status file it it doesn't exist already, this takes the pool names from the treshold file and gives them a generic machine with no data

    # Load data from the config file
    with open(CONFIG_FILE_PATH, 'r') as f:
        config_data = json.load(f)

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
            "machine_count": 1,  # Initially one machine in every pool
            "last_action_timestamp": formatted_time,
            "timer_timestamp_in_epoch": current_time,
            "last_action_performed": "no_data",
            "machines" : {
                "1": {
                    "creation_date": formatted_time,
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
def load_thresholds(): #open the treshold config file and grab its contents
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            thresholds = json.load(file) 
        return thresholds
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE_PATH}' not found.")
        exit(1)

####################################################################################################################################

#PARSE LINES
def parse_load_averages(line):
    #given the line that the agent sends it separates it in single elements so that i can work with it
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

# CHECK OUTSCALE / INSCALE / TIMER
def check_load(thresholds, data, start_time):
    #use the parse function and send the data for each load to check to the singl load check
    
    line_data = parse_load_averages(data)
    log_action(f"Checking 1-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
    check_single_load(line_data[2], thresholds[line_data[0]]['THRESHOLD_LOW_1MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_1MIN'], line_data, start_time)

    log_action(f"Checking 5-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
    check_single_load(line_data[3], thresholds[line_data[0]]['THRESHOLD_LOW_15MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_15MIN'], line_data, start_time)

    log_action(f"Checking 15-Minute load average of the machine {line_data[1]}, from the pool {line_data[0]}, {line_data[2], line_data[3], line_data[4]}")
    check_single_load(line_data[4], thresholds[line_data[0]]['THRESHOLD_LOW_5MIN'], thresholds[line_data[0]]['THRESHOLD_HIGH_5MIN'], line_data, start_time)


####################################################################################################################################

#SINGLE CHECK
def check_single_load(load_avg, threshold_low, threshold_high, line_data, start_time):
    #2 major checks into 2 lower checks the first 2 ones are for: "over threshold loads", "lower then threshold loads"
    #the other 2 are if the machine number is within 1 and 10, if the timer is still running and then i can actually perform the action
    if load_avg > threshold_high:
        log_action("The load average is higher then the tresholds, outscaling needed")
        if check_machine_number(line_data[0]) >= 10:
            log_action("Max number of machines reached, outscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - start_time):.3f} secondi\n")
        elif check_status_timer(line_data[0]):
            update_status(line_data[0], line_data[1], "outscale", [line_data[2], line_data[3], line_data[4]])
            perform_outscale(start_time)
        else:
            log_action("Timer in progress, outscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - start_time):.3f} secondi\n")
        
    elif load_avg < threshold_low:
        log_action("The load average is below the tresholds, inscale needed")
        if check_machine_number(line_data[0]) <= 1:
            log_action("There is only 1 machine in the pool, inscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - start_time):.3f} secondi\n")
        elif check_status_timer(line_data[0]):
            update_status(line_data[0], line_data[1], "inscale", [line_data[2], line_data[3], line_data[4]])
            perform_inscale(start_time)
        else:
            log_action("Timer in progress inscale aborted")
            update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
            current_time = float(f"{time.time():.3f}")
            log_action(f"Check terminated in {(current_time - start_time):.3f} secondi\n")
    else: #if the 2 checks come clean the machine is within the tresholds so there is nothing to do other then logging and updating the status
        log_action("The load average is within the tresholds, nothing to do")
        update_status(line_data[0], line_data[1], "nothing", [line_data[2], line_data[3], line_data[4]])
        current_time = float(f"{time.time():.3f}")
        log_action(f"Check terminated in {(current_time - start_time):.3f} secondi\n")


####################################################################################################################################

# OUTSCALE
def perform_outscale(start_time):
    #doesnt actually perform the outscale yet but makes the code work as if it actually did
    log_action("Performing outscale")
    print("Outscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Outscale done successfully")
    log_action(f"Outscale terminated in {(current_time - start_time):.3f} secondi\n")

####################################################################################################################################

# INSCALE
def perform_inscale(start_time):
    #doesnt actually perform the insale yet but makes the code work as if it actually did
    log_action("Performing inscale")
    print("Inscaling")
    # Record last action time
    current_time = float(f"{time.time():.3f}")
    log_action("Inscale done successfully")
    log_action(f"Inscale terminated in {(current_time - start_time):.3f} secondi\n")

####################################################################################################################################


def main(data, agent): #main function that start for each string of data sent to the master by the agents
    
    log_action("Scaling_Check_Sevice Started\n")

    start_time = float(f"{time.time():.3f}") # timestamp to use to get the execution time

    if not os.path.exists(STATUS_FILE_PATH): #create status if it doesnt exist
        create_status_file_from_config()

    # Grab thresholds
    thresholds = load_thresholds() #grab the tresholds

    check_load(thresholds, data, start_time) #start the check with

    #write in the logs that the check actually terminated
    log_action(f"Check for {agent} terminated\n")
    return "done"

####################################################################################################################################

# Function to handle communication with each agent
async def handle_client(reader, writer):
    # Read up to 1024 bytes of data sent by the client (agent)
    data = await reader.read(1024)  # Asynchronously read data from the client
    message = data.decode('utf8')  # Decode
    addr = writer.get_extra_info('peername')  # Retrieve the client's address (IP and port)

    # Print the received message and the client's address for debugging/monitoring
    print(f"Received data: {message} from {addr}")

    # Process the received message and prepare a response using the 'main' function
    response = main(message, addr)
    writer.write(response.encode())  # Asynchronously send the response back to the client (encoded as bytes)
    
    # Wait until the response is fully sent to the client (drain the output buffer)
    await writer.drain()

    # Log that the communication with the client is finished
    print("Closing the connection")

    # Close the connection with the client
    writer.close()

# Function to start the server that listens for incoming client connections
async def start_master_server():
    # Create and start the server that listens on all available network interfaces (0.0.0.0)
    # and binds to port 6969
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 6969)  # Asynchronously start the server

    # Retrieve the address (IP and port) the server is bound to
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    # Main loop 
    async with server:
        await server.serve_forever()

#
if __name__ == '__main__':
    asyncio.run(start_master_server())  # Start the asynchronous server
