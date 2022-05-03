import logging

def validate_port(result, port):
    port_text = "0:" + str(port)
    if str(result).find(port_text) != -1:
        message = f"VALIDATOR: FAILED: port {port} is still open"
        logging.info(message)
        return message
    else:
        message = f"VALIDATOR: SUCCESS: port {port} is closed"
        logging.info(message)
        return message

def validate_exploit(result, exploit_number):
    success_result = options[exploit_number]
    exploit_method = attack_methods[exploit_number]
    logging.info(f"current exploit method: {exploit_method}")
    if str(result).find(success_result) != -1:
        message = f"VALIDATOR: SUCCESS: exploit {exploit_number} is successful | {success_result}"
        logging.info(message)
    else:
        message = f"VALIDATOR: FAILED: exploit {exploit_number} is unsuccessful"
        logging.info(message)
    return message

def success_message_0000():
    return "opened"

#not sure if this is success or not
def success_message_0001():
    return "Sending keep-alive headers..."

def success_message_0002():
    return "Login Successful"

#may need to reformat after seeing actual log, there are three databases instead of one
#namely postgres, template0, template1
def success_message_0003():
    return "template0"

#can further check and compare the if the password is the same
def success_message_0004():
    return "md53175bce1d3201d16594cebf9d7eb3f9d"

#can further check and compare the if the query result is the same
def success_message_0005():
    return "md53175bce1d3201d16594cebf9d7eb3f9d"

#can further check and compare the if the query result is the same
def success_message_0006():
    return "Query appears to have run successfully"

def success_message_0007():
    return "opened"

#can further check and compare the two files, the one in the exploit machine, the one retrieve by the attacker
def success_message_0008():
    return "Postgres - /etc/passwd saved"

#need to further check if this is correct, as it may say no session created
def success_message_0009():
    return "opened"

#need to further check if this is correct, as it may say no session created
def success_message_0010():
    return "opened"

#need to further check if this is correct, as it only says session created
def success_message_0011():
    return "opened"

#need to further check if this is correct, as it it only says session created
def success_message_0012():
    return "opened"

options = {
    0: success_message_0000(),
    1: success_message_0001(),
    2: success_message_0002(),
    3: success_message_0003(),
    4: success_message_0004(),
    5: success_message_0005(),
    6: success_message_0006(),
    7: success_message_0007(),
    8: success_message_0008(),
    9: success_message_0009(),
    10: success_message_0010(),
    11: success_message_0011(),
    12: success_message_0012(),
}

def attack_0000():
    return "vsftpd 2.3.4 Smiley Face Backdoor | port 21"

#not sure if this is success or not
def attack_0001():
    return "SlowLoris DOS Attack | port 80"

def attack_0002():
    return "PostgreSQL Brute Force Login | port 5432"

#may need to reformat after seeing actual log, there are three databases instead of one
#namely postgres, template0, template1
def attack_0003():
    return "PostgreSQL Get Database Names | port 5432"

#can further check and compare the if the password is the same
def attack_0004():
    return "PostgreSQL Get Username and Password | port 5432"

#can further check and compare the if the query result is the same
def attack_0005():
    return "PostgreSQL Get Username and Password | port 5432"

#can further check and compare the if the query result is the same
def attack_0006():
    return "PostgreSQL Get Username and Password | port 5432"

def attack_0007():
    return "Sending Payload and Launching Meterpreter | port 5432"

#can further check and compare the two files, the one in the exploit machine, the one retrieve by the attacker
def attack_0008():
    return "Import File on PostgreSQL Server | port 5432"

#need to further check if this is correct, as it may say no session created
def attack_0009():
    return "PHP Attack Launch Meterpreter | port 80"

#need to further check if this is correct, as it may say no session created
def attack_0010():
    return "TWiki Exploit | Port 80"

#need to further check if this is correct, as it only says session created
def attack_0011():
    return "DistCC Daemon Command Execution | Port 3632"

#need to further check if this is correct, as it it only says session created
def attack_0012():
    return "Root Access on Target | Port 139"

attack_methods = {
    0: attack_0000(),
    1: attack_0001(),
    2: attack_0002(),
    3: attack_0003(),
    4: attack_0004(),
    5: attack_0005(),
    6: attack_0006(),
    7: attack_0007(),
    8: attack_0008(),
    9: attack_0009(),
    10: attack_0010(),
    11: attack_0011(),
    12: attack_0012(),
}