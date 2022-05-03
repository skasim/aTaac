import xml.etree.ElementTree as ET
import pickle
import pandas as pd
import random
import os
import docker_move
from dotenv import load_dotenv
import logging
import validator

load_dotenv()
root_path = os.getenv("ROOT_PATH")
commands_file = os.getenv("COMMANDS_CSV")
vulnerability_scripts_dir = os.getenv("VULNERABILITY_SCRIPTS_DIR")
portscan_xml_file = os.getenv("PORTSCAN_XML")
attack_ports_pk = os.getenv("ATTACK_PORTS_PK")
attacker = os.getenv("ATTACK")
defender = os.getenv("DEFENSE")
script_dir = os.getenv("VULNERABILITY_SCRIPTS_DIR")

port_mapping = {21: "ftp",
                22: "ssh",
                23: "telnet",
                25: "smtp",
                53: "domain",
                80: "http",
                111: "rpcbind",
                139: "netbios-ssn",
                445: "microsoft-ds",
                512: "exec",
                513: "login",
                514: "shell",
                1099: "rmiregistry",
                1524: "ingreslock",
                2049: "nfs",
                2121: "ccproxy-ftp",
                3306: "mysql",
                5432: "postgresql",
                5900: "vnc",
                6000: "X11",
                6667: "irc",
                8009: "ajp13",
                8180: "unknown"}

id_port_mapping = {0: 21,
                   1: 80,
                   2: 5432,
                   3: 5432,
                   4: 5432,
                   5: 5432,
                   6: 5432,
                   7: 5432,
                   8: 5432,
                   9: 80,
                   10: 80,
                   11: 3632,
                   12: 139}


class ScriptLauncher:
    def __init__(self):
        self.current_attack_id = 0
        self.attack_port = ""
        self.attacked_process = ""

    def parse_nmaprun_xml(self, fname):
        xml_tree = ET.parse(fname)
        root = xml_tree.getroot()
        outports = []
        for child in root:
            for nmap_child in root.iter(child.tag):
                if nmap_child.tag == "host":
                    for elem in nmap_child:
                        if elem.tag == "ports":
                            for ports in elem:
                                if ports.tag == "port":
                                    for port in ports:
                                        port = {
                                            "port_id": ports.attrib["portid"],
                                            "protocol": ports.attrib["protocol"],
                                            "service_name": port.attrib["name"] if "name" in port.attrib else None}
                                    outports.append(port)
        return outports

    def common(self, open_ports):
        commands = pd.read_csv(f"{root_path}/{commands_file}")
        command_ports = commands["linked_port"].tolist()
        command_ports = sorted(list(set(command_ports)))

        open_ports_set = set(open_ports)
        intersection = open_ports_set.intersection(command_ports)
        return sorted(list(intersection))

    # currently prints the file contents, can be repurposed to run them through msfconsole
    def get_rc(self, c, script_id, step):
        file = open(
            f"{root_path}/{vulnerability_scripts_dir}/{script_id}_{step}.rc", "r")
        print(file.read().splitlines())

    def get_command(self, c, attack, defense, docker, verbose):

        if c == 0:
            # use os or subprocess library to launch scripts?
            print("Port scan on target machine using Nmap...")
            if docker == 1:
                docker_move.get_nmap(attack)

        else:
            if self.current_attack_id < 10:
                script_id = "000{0}".format(self.current_attack_id)
            else:
                script_id = "00{0}".format(self.current_attack_id)

            if c == 1:
                # use os or subprocess library to launch scripts?
                command = f"msfconsole --quiet -r /{script_dir}/{script_id}_use.rc"
                logging.debug(command)
                if docker == 0:
                    self.get_rc(c, script_id, "use")
                else:
                    result = docker_move.cyber_move(
                        player=1, command=command, attack=attack, defense=defense, verbose=verbose)

            elif c == 2:
                # use os or subprocess library to launch scripts?
                command = f"msfconsole --quiet -r /{script_dir}/{script_id}_use+set.rc"
                logging.debug(command)
                if docker == 0:
                    self.get_rc(c, script_id, "set")
                else:
                    result = docker_move.cyber_move(
                        player=1, command=command, attack=attack, defense=defense, verbose=verbose)

            elif c == 3:
                # use os or subprocess library to launch scripts?
                command = f"/{script_dir}/{script_id}.sh"
                logging.debug(command)
                if docker == 0:
                    self.get_rc(c, script_id, "exploit")
                else:
                    result = docker_move.cyber_move(
                        player=1, command=command, attack=attack, defense=defense, verbose=verbose)
                    validator.validate_exploit(result, self.current_attack_id)

            elif c == 4:
                port = self.attack_port
                process = self.attacked_process
                command = f'fuser -k {port}/tcp'
                logging.info(
                    "Kill process *{0}* on port *{1}*".format(process, port))
                if docker == 1:
                    result = docker_move.cyber_move(
                        player=2, command=command, attack=attack, defense=defense, verbose=verbose)
                    validator.validate_port(result, port)

            elif c == 5:
                logging.info("Kill daemon")
                logging.info("VALIDATOR: SUCCESS: server shut down")

    def launch_script(self, command, defender_skill_level, attack, defense, docker, verbose):
        # debug mode on
        verbose = True

        num_ports_open = {
            5: random.randint(0, 3),
            4: 4,
            3: 7,
            2: 11,
            1: 12,
            0: 13
        }
        print("Launch script process commenced:")
        # scan command
        if command == 0:

            self.get_command(c=command, attack=attack,
                             defense=defense, docker=docker, verbose=verbose)

            # parse nmap xml output
            parsed = self.parse_nmaprun_xml(f"{root_path}/{portscan_xml_file}")
            ports = []

            # get all open ports
            for port in parsed:
                ports.append(int(port["port_id"]))

            # find common ports between those that are open and those that we have attacks for
            common_ports = self.common(ports)
            logging.info(
                f"{len(common_ports)} true open ports, {common_ports}")

            # shuffle open, common ports
            # this is done so that the attacker picks a random port to attack when starting out
            random.shuffle(common_ports)
            # number of ports to return based on the defender skill level
            common_ports = common_ports[: num_ports_open[defender_skill_level]]
            print(f"{len(common_ports)} open ports on target system: {common_ports}")
            logging.info(
                f"{len(common_ports)} open ports on target system: {common_ports}")

            # write open common ports to pickle file
            with open(f"{root_path}/{attack_ports_pk}", "wb") as f:
                pickle.dump(common_ports, f)

        # use command
        elif command == 1:
            # load open, common ports to attack
            with open(f"{root_path}/{attack_ports_pk}", "rb") as f:
                common_ports = pickle.load(f)

            # pick first port from list
            self.attack_port = common_ports.pop(0)

            # save list of ports again, without the current attack port
            with open(f"{root_path}/{attack_ports_pk}", "wb") as f:
                pickle.dump(common_ports, f)

            # get services to attack from commands db, find available attacks for port intended to attack
            valid_attacks = pd.read_csv(f"{root_path}/{commands_file}")
            attacks_for_current_port = valid_attacks[valid_attacks["linked_port"]
                                                     == self.attack_port]

            # of the possible attacks to mount given the current port, pick 1 at random and get corresponding process on port
            self.current_attack_id = attacks_for_current_port.sample(n=1)[
                "attack_id"].to_list()[0]
            self.attacked_process = port_mapping[self.attack_port]

            logging.info("Attack ID *{0}*, attacking service *{1}* on port *{2}*".format(self.current_attack_id,
                                                                                         self.attacked_process,
                                                                                         self.attack_port))

            self.get_command(c=command, attack=attack,
                             defense=defense, docker=docker, verbose=verbose)

        else:
            '''
            c == [2] --> set command
            c == [3] --> exploit command
            c == [4] --> kill process command
            c == [5] --> kill daemon command
            '''
            self.get_command(c=command, attack=attack,
                             defense=defense, docker=docker, verbose=verbose)
