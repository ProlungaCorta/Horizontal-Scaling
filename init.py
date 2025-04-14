import docker
import json
import os
import time

# Load threshold configuration
with open("threshold.conf", "r") as f:
    threshold_config = json.load(f)

client = docker.from_env()

def ensure_network_exists(network_name):
    networks = client.networks.list(names=[network_name])
    if not networks:
        print(f"Creating Docker network '{network_name}'...")
        client.networks.create(network_name, driver="bridge")
    else:
        print(f"Docker network '{network_name}' already exists.")

def build_images():
    print("Building master image...")
    client.images.build(path=".", dockerfile="Dockerfile.master", tag="master")

    for pool in threshold_config:
        image_tag = f"agent_{pool}_1"
        print(f"Building image for agent '{pool}'...")
        client.images.build(path=".", dockerfile="Dockerfile.agent", tag=image_tag)

def get_master_ip(container_name):
    master_container = client.containers.get(container_name)
    master_network = master_container.attrs["NetworkSettings"]["Networks"]["my_network"]
    return master_network["IPAddress"]

def create_master_container():
    print("Creating master container...")
    return client.containers.run(
        "master",
        detach=True,
        name="master",
        network="my_network",
        volumes={
            os.path.abspath("threshold.conf"): {
                'bind': '/app/threshold.conf',
                'mode': 'ro'
            },
            "/var/run/docker.sock": {  # Mounting Docker socket
                'bind': '/var/run/docker.sock',
                'mode': 'rw'  # Read-Write mode so the container can interact with Docker
            }
        },
        working_dir="/app"
    )


def create_agent_containers(master_ip):
    for pool in threshold_config.keys():
        print(f"Creating agent container for pool: {pool}...")

        config_filename_host = f"config_{pool}_1.json"

        config_data = f'pool: {pool}, id: 1, ip: {master_ip}, port: 6969'

        time.sleep(1)
        
        client.containers.run(
            f"agent_{pool}_1",
            detach=True,
            name=f"agent_{pool}_1",
            network="my_network",
            environment={
                'CONFIG_DATA': config_data  # Pass config as an environment variable
            },
            #command=["/bin/sh", "-c", "env && sleep 60"],
            command=["python3", "agent.py"],
            working_dir="/app"
        )

def main():
    ensure_network_exists("my_network")
    build_images()
    
    master_container = create_master_container()

    # Allow time for master to start and join the network
    time.sleep(2)

    master_ip = get_master_ip("master")
    print(f"Master IP: {master_ip}")
    time.sleep(5)
    create_agent_containers(master_ip)
    print("All containers started successfully.")
    

if __name__ == "__main__":
    main()
