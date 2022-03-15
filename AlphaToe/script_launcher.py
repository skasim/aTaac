import xml.etree.ElementTree as ET
import pickle
import pandas as pd
import random
import os
from dotenv import load_dotenv

load_dotenv()


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


class Evaluations:
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
        commands = pd.read_csv("./io/commands2.csv")
        command_ports = commands["linked_port"].tolist()
        command_ports = sorted(list(set(command_ports)))

        open_ports_set = set(open_ports)
        intersection = open_ports_set.intersection(command_ports)
        return sorted(list(intersection))

    # currently prints the file contents, can be repurposed to run them through msfconsole
    def get_rc(self, c, script_id, step):
        file = open("./io/vulnerability_scripts/{0}/{0}_{1}.rc".format(script_id, step), "r")
        print(file.read().splitlines())

    def get_command(self, c):

        if c == 0:
            # use os or subprocess library to launch scripts?
            print("Port scan on target machine using Nmap...")
            print("./nmap.sh")

        else:
            if self.current_attack_id < 10:
                script_id = "000{0}".format(self.current_attack_id)
            else:
                script_id = "00{0}".format(self.current_attack_id)

            if c == 1:
                # use os or subprocess library to launch scripts?
                print("msfconsole -r {0}_use.rc".format(script_id))
                self.get_rc(c, script_id, "use")

            elif c == 2:
                # use os or subprocess library to launch scripts?
                print("msfconsole -r {0}_set.rc".format(script_id))
                self.get_rc(c, script_id, "set")

            elif c == 3:
                # use os or subprocess library to launch scripts?
                print("msfconsole -r {0}_exploit.rc".format(script_id))
                self.get_rc(c, script_id, "exploit")

            elif c == 4:
                port = self.attack_port
                process = self.attacked_process
                print("Kill process *{0}* on port *{1}*".format(process, port))

            elif c == 5:
                print("Kill daemon")

    def launch_script(self, command):

        # scan command
        if command == 0:

            self.get_command(command)

            # parse nmap xml output
            parsed = self.parse_nmaprun_xml("./io/nmap/portscan_out.xml")
            ports = []

            # get all open ports
            for port in parsed:
                ports.append(int(port["port_id"]))

            # find common ports between those that are open and those that we have attacks for
            common_ports = self.common(ports)

            # shuffle open, common ports
            # this is done so that the attacker picks a random port to attack when starting out
            random.shuffle(common_ports)

            # write open common ports to pickle file
            with open("./io/attack_ports.pickle", "wb") as f:
                pickle.dump(common_ports, f)

        # use command
        elif command == 1:
            # load open, common ports to attack
            with open("./io/attack_ports.pickle", "rb") as f:
                common_ports = pickle.load(f)

            # pick first port from list
            self.attack_port = common_ports.pop(0)

            # save list of ports again, without the current attack port
            with open("./io/attack_ports.pickle", "wb") as f:
                pickle.dump(common_ports, f)

            # get services to attack from commands db, find available attacks for port intended to attack
            valid_attacks = pd.read_csv("./io/commands2.csv")
            attacks_for_current_port = valid_attacks[valid_attacks["linked_port"] == self.attack_port]

            # of the possible attacks to mount given the current port, pick 1 at random and get corresponding process on port
            self.current_attack_id = attacks_for_current_port.sample(n=1)["attack_id"].to_list()[0]
            self.attacked_process = port_mapping[self.attack_port]

            print("Attack ID *{0}*, attacking service *{1}* on port *{2}*".format(self.current_attack_id,
                                                                                  self.attacked_process,
                                                                                  self.attack_port))

            self.get_command(command)

        else:
            '''
            c == [2] --> set command
            c == [3] --> exploit command
            c == [4] --> kill process command
            c == [5] --> kill daemon command
            '''
            self.get_command(command)