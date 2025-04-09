import socket
import time
import subprocess
import json

ACTION_LOG_FILE = "logs"  #path to the log file 
CONFIG_FILE_PATH = "config.json" #path of the config file where pool and id are located

####################################################################################################################################



# LOAD AVERAGES
def get_load_averages():   
    #use the subprocess library to grab the output of the uptime command and then parse it in the 3 variables i need (1minute, 5minute, 15 minute averages)
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



# LOGGING
def log_action(message):  #open the log file and append the message with the current timestamp
    with open(ACTION_LOG_FILE, 'a') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        log_file.write(f"{timestamp} - {message}\n")



####################################################################################################################################



#GRAB DATA
def get_data():  #open the config file to extract the pool, id, ip of the master and the port
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            data = json.load(file) 
        return data
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE_PATH}' not found.")
        exit(1)



####################################################################################################################################



#PREPARE DATA
def data_to_send(config_data):  #proc the needed functions and prepare the string with all the data to be sent
    averages = get_load_averages()
    config_data
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    log_action(f"current loads: \n{timestamp} - {config_data['pool']} - {config_data['id']} - {averages[0]}, {averages[1]}, {averages[2]}")
    return f"{timestamp} - {config_data['pool']} - {config_data['id']} - {averages[0]}, {averages[1]}, {averages[2]}"



####################################################################################################################################



# SEND DATA TO THE MASTER
def send_data_to_master(data, host, port):
    # Create a socket object using IPv4 (AF_INET) and a TCP socket type (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the master script (server) at the specified host and port
            client_socket.connect((host, port))
            
            # Send the provided data after encoding it to UTF-8
            client_socket.sendall(data.encode('utf-8'))
            
            # Print a message to indicate that the data was sent successfully
            log_action("Data sent successfully")
            print(f"Sent data to master: {data}")
        except Exception as e: #error if connection fails
            print(f"Error connecting to master: {e}")




####################################################################################################################################



# CODE START AND MAIN LOOP
if __name__ == "__main__":
    while True:
        # Send the data to the master script
        log_action("Starting the data upload")
        config_data = get_data()
        data = data_to_send(config_data)
        send_data_to_master(data, config_data['ip'], int(config_data["port"]))
        # Wait before sending data again
        time.sleep(60)
