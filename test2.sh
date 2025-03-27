#!/bin/bash

# Load the thresholds
source ./threshold.conf
echo $pool_type
# Menu
case $pool_type in
    "Low")
        # Load Low Thresholds
        eval "${web[@]}"
        ;;
    "Medium")
        # Load Medium Thresholds
        eval "${db[@]}"
        ;;
    "High")
        # Load High Thresholds
        eval "${monit[@]}"
        ;;
esac
echo $THRESHOLD_HIGH_1MIN
# Timer file
LAST_RUN_FILE="/tmp/last_run_time"

# Function for upscale
perform_upscale() {
    echo "Upscaling"
}

# Function for downscale
perform_downscale() {
    echo "Downscaling"
}

# Get the current time in seconds
current_time=$(date +%s)

# Check if the last run file exists and read the last run time
if [[ -f "$LAST_RUN_FILE" ]]; then
    last_run_time=$(cat "$LAST_RUN_FILE")
else
    last_run_time=0
fi

# Fetch the load averages from the uptime command
# Extract 1-minute, 5-minute, and 15-minute load averages from the uptime output
load_avg_1min=$(uptime | awk -F'load average: ' '{ print $2 }' | awk '{ print $1 }' | tr -d ',')
load_avg_5min=$(uptime | awk -F'load average: ' '{ print $2 }' | awk '{ print $2 }' | tr -d ',')
load_avg_15min=$(uptime | awk -F'load average: ' '{ print $2 }' | awk '{ print $3 }' | tr -d ',')

# Debugging: Check the load average values
echo "1-minute Load average: $load_avg_1min"
echo "5-minute Load average: $load_avg_5min"
echo "15-minute Load average: $load_avg_15min"

# Function to check and perform actions based on load average
check_load() {
    local load_avg=$1
    local threshold_high=$2
    local threshold_low=$3
    local time_diff=$4
    echo $load_avg
    echo $threshold_high
    echo "$load_avg > $threshold_high"
    if (( $(echo -n "$load_avg > $threshold_high" | bc -l) )) && (( time_diff >= 300 )); then
        perform_upscale
        echo "$current_time" > "$LAST_RUN_FILE"
    elif (( $(echo -n "$load_avg < $threshold_low" | bc -l) )) && (( time_diff >= 300 )); then
        perform_downscale
        echo "$current_time" > "$LAST_RUN_FILE"
    elif (( time_diff < 300 )); then
        echo "Timer in progress, please wait"
    fi
}

# Perform checks for 1-minute, 5-minute, and 15-minute load averages
check_load "$load_avg_1min" "$THRESHOLD_HIGH_1MIN" "$THRESHOLD_LOW_1MIN" "$((current_time - last_run_time))"
check_load "$load_avg_5min" "$THRESHOLD_HIGH_5MIN" "$THRESHOLD_LOW_5MIN" "$((current_time - last_run_time))"
check_load "$load_avg_15min" "$THRESHOLD_HIGH_15MIN" "$THRESHOLD_LOW_15MIN" "$((current_time - last_run_time))"
