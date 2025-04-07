# Horizontal Scaling

This repository contains a Python-based project aimed at implementing horizontal scaling techniques. The project is designed to illustrate the concept of scaling resources to handle increasing and decreasing loads by distributing the workload across multiple machines.

## Contents

- **Master Node**: Takes the load data from the agents and processes it to either perform an outscale or an inscale if needed.
- **Agent Nodes**: Finds the load averages of the machine it is in and sends it to the Master.

## Files

- `master.py`: The master node controller that performs the checks from the data from the agents.
- `agent.py`: The agent nodes that send data to the master.
- `status.json`: Stores the status of the system components.
- `threshold.conf`: Configuration file for setting scaling thresholds and pool names.
- `action_log.txt`: Logs the actions and events that occur in the system.

## Setup

### Prerequisites
- Python 3.x

### Installation

Clone the repositoryin your Master machine:

    git clone https://github.com/ProlungaCorta/Horizontal-Scaling.git

Move the contents of the agent folder in your agent machine.
Edit the config.json and the thresolds.json with your data and you're done.
