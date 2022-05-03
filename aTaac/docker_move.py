import os
import docker
from time import sleep 
import logging

from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
attack = os.getenv('ATTACK')
defense = os.getenv('DEFENSE')
root_path = os.getenv('ROOT_PATH')
portscan_full_path = os.getenv('PORTSCAN_XML')
network_name = "adversarial"
is_docker = int(os.getenv("DOCKER"))
if is_docker == 1:
    client = docker.from_env()


# In[1]:

def wait_for_container_to_start(container):
    
    timeout = 120
    stop_time = 3
    elapsed_time = 0

    while container.status != 'running' and elapsed_time < timeout:
        print(container.status)
        logging.info(container.status)
        sleep(stop_time)
        elapsed_time += stop_time
        print("waiting...", container.name)
        logging.info(f"waiting...{container.name}")
        continue
    
    if elapsed_time >= timeout:
        return False
    
    return True

def run_command_to_target(source: str, target: str, command: str):
    logging.debug(f"operating container: {source.name}")
    #need stdin and tty to execute commands simutaneously
    result = target.exec_run(f"netstat -tulnp | grep LISTEN")
    logging.debug(f"target opened port: {result}")
    result = source.exec_run( f"bash -c '{command}; sleep 10; exit'")
    logging.debug(f"operation_result: {result}")
    return result

# %%


def run_command_to_self(source: str, command: str):
    logging.debug(f"operating container: {source.name}")
    #need stdin and tty to execute commands simutaneously
    result = source.exec_run( f"{command}")
    logging.debug(f"kill_process_result: {result}")
    result = source.exec_run( f"netstat -tulnp | grep LISTEN")
    logging.debug(f"validation_result: {result}")
    return result


# %%
def cyber_move(player, command, attack, defense, verbose):
    if player == 1:
        result = run_command_to_target(attack, defense, command)
    else:
        result = run_command_to_self(defense, command)
    return result

# %%
def start_game_docker(docker):
    if docker != 1:
        return "attack", "defense"
    print("stopping existing containers...")
    logging.info("stopping existing containers...")
    for container in client.containers.list():
        container.stop()
    client.containers.prune()
    client.networks.prune()
    print("start process...")
    docker_network = client.networks.create(network_name)
    attack_container = client.containers.run(attack, detach=True, auto_remove=True, network=docker_network.id, stdin_open=True, name=attack)
    defense_container = client.containers.run(defense, detach=True, auto_remove=True, network=docker_network.id, stdin_open=True, name=defense, cap_add=["SYS_PTRACE"], security_opt=["apparmor:unconfined"])
    print("setup done")

    return attack_container, defense_container
 
# %%
def end_game_docker():
    if is_docker == 0:
        return None
    client.containers.prune()

# %%
def get_nmap(attack_container):
    container_name = attack_container.name
    portscan_path = portscan_full_path.split('/')[0]
    portscan_file_name = portscan_full_path.split('/')[1]
    attack_container.exec_run( f"nmap -oX {portscan_file_name} {defense}")
    os.system(f'docker cp {container_name}:/{portscan_file_name} {root_path}/{portscan_path}')
