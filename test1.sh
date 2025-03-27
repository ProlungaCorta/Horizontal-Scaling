#!/bin/bash

# thresholds
LOAD_THRESHOLD_HIGH=1.0
LOAD_THRESHOLD_LOW=0.2


# timer file
LAST_RUN_FILE="/tmp/last_run_time"

# funzione per upscale
perform_upscale() {
    echo "Upscaling"
}

# funzione per downscale
perform_downscale() {
    echo "Downscaling"
}

# Get current time in seconds
current_time=$(date +%s)

# Check if last run file exists and read the last run time
if [[ -f "$LAST_RUN_FILE" ]]; then
    last_run_time=$(cat "$LAST_RUN_FILE")
else
    last_run_time=0
fi

# Get the 1-minute load average
load_avg=$(uptime | awk -F'load average: ' '{ print $2 }' | awk '{ print $1 }' | tr -d '[:space:],')
echo $load_avg
# Debugging: Check the load average value
echo "Load average: $load_avg"


# Upscale check
if (( $(echo "$load_avg > $LOAD_THRESHOLD_HIGH" | bc -l) )) && (( current_time - last_run_time >= 300 )); then
    perform_upscale
    echo "$current_time" > "$LAST_RUN_FILE"

# Downscale check
elif (( $(echo "$load_avg < $LOAD_THRESHOLD_LOW" | bc -l) )) && (( current_time - last_run_time >= 300 )); then
    perform_downscale
    echo "$current_time" > "$LAST_RUN_FILE"

# Timer check for when function is still running
elif (( current_time - last_run_time < 300 )); then
    echo "Timer in progress, please wait"
fi