import sys
from typing import List, Dict
import mapping as mp
from dotenv import load_dotenv
import os
import pandas as pd
from pprint import pprint
from script_launcher import ScriptLauncher
import logging

sys.path.insert(1, os.getcwd())

load_dotenv()
xml_file = f"{os.getenv('ROOT_PATH')}/{os.getenv('PORTSCAN_XML')}"
commands_csv = f"{os.getenv('ROOT_PATH')}/{os.getenv('COMMANDS_CSV')}"
attacks = pd.read_csv(commands_csv)

metasploit = {
    0: "scan_command",
    1: "use_command",
    2: "set_command",
    3: "exploit_command",
    4: "kill_process_command",
    5: "kill_daemon_command",
    6: "nop_command",
}


# ## get_state_mapping_evaluation
#
# Main method for the graph traversal program. Takes in a previous and current state and returns the action performed in the cyber realm.
# * **prev_state**: The previous state of the game board.
# * **current_state**: The current state of the game board.
# * **debug**: Bool flag to print debug statements.
#
# **returns**: List[int].

def get_state_mapping_evaluation(prev_state: List[List[int]], current_state: List[List[int]],
                                 exploit_tracker: Dict[str, bool], debug: bool = False):
    move = mp.get_latest_move(prev_state, current_state)
    i = move[0]
    j = move[1]
    if current_state[i][j] == 1:  # attacker
        if debug:
            print("attacker move")
            logging.info("attacker move")
        if len(current_state) == 3:
            command = mp.eval_attacker_3x3(
                i, j, current_state, exploit_tracker, debug)
        if len(current_state) == 5:
            command = mp.eval_attacker_5x5(
                i, j, current_state, exploit_tracker, debug)
    elif current_state[i][j] == 2:  # defender
        if debug:
            print("defender move")
            logging.info("defender move")
        if len(current_state) == 3:
            command = mp.eval_defender_3x3(
                i, j, current_state, exploit_tracker, debug)
        if len(current_state) == 5:
            command = mp.eval_defender_5x5(
                i, j, current_state, exploit_tracker, debug)
    else:
        raise ValueError(f"unexpected game value: ({i}, {j})")  # ruh roh
    return command


# ## eval_move
#
# Method to transform for metasploit scripts.
# * **prev_state**: The previous state of the game board.
# * **current_state**: The current state of the game board.
# * **debug**: Bool flag to print debug statements.
#
# **returns**: str.

# In[22]:

def eval_move(prev_state: List[List[int]], current_state: List[List[int]],
              exploit_tracker: Dict[str, bool], launcher: ScriptLauncher,
              defender_skill_level: int, attack_container, defense_container, docker: int, debug: bool = False, ) -> List[str]:
    command = get_state_mapping_evaluation(
        prev_state, current_state, exploit_tracker, debug)
    for c in command:
        try:
            launcher.launch_script(command=c, defender_skill_level=defender_skill_level,
                                   attack=attack_container, defense=defense_container, docker=docker, verbose=debug)
        except IndexError:  # popping from an empty list, i.e. no open ports
            launcher.launch_script(command=0, defender_skill_level=defender_skill_level,
                                   attack=attack_container, defense=defense_container, docker=docker, verbose=debug)
            return[metasploit[0]]
    return [metasploit[c] for c in command]
