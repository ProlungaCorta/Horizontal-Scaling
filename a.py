import json

config_file = "threshold2.conf"

with open(config_file, 'r') as file:
            config = json.load(file) 
            
            web_t = config["Web"]
            print(web_t)
            print(web_t['THRESHOLD_LOW_1MIN'])