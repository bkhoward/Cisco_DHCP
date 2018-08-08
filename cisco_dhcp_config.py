#!/usr/bin/env python
#
#  Author:   Brian Howard
#  Date:     11JUL2018
#  Version:  1.0
#  Abstract: Create SSH connection to Cisco device. Capture DHCP Pool info and modify
#            DNS servers within each DHCP Pool to new IP addresses. Generate a Log file
#            for each host
#
#  Source Files:
#           cisco_dhcp_config.py - main file
#           credentials.py - file to store login credentials
#           host_file.py - python list containing ip addresses of cisco hosts
#           dns_srv_file.py - python list containing dns server IPs that will replace the dhcp scope
#           show_cmd_file.py - python list containing cisco show commands to run within the script
#                   Note: 'show run | include hostname' must be element 0
#                         'show run | section ip dhcp pool' must be element 1
#
#  Output Files:
#           Log.log - complete log file captures during life of script
#           log_{hostname}.log - log file of interaction with each host
#           dhcp_{hostname}.txt - list of dhcp pool names scraped from config
# ------------------------------------------------------------------------------------------------#


# ------------------------------------------------------------------------------------------------#
# Function definitions
# ------------------------------------------------------------------------------------------------#

import logging
# from importlib import reload
from show_cmd_file import show_cmd_list
from dns_srv_file import dns_srv_list
from host_file import host_list
from credentials import UN, PW
from netmiko import ConnectHandler

Log_File_handler = logging.FileHandler(filename='Log.log')
console_handler = logging.StreamHandler()
handlers = [Log_File_handler, console_handler]

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('Log File')


def get_hostname(hostname_cmd, session):
    hname = session.send_command(hostname_cmd)
    hname = hname.split(" ")
    return hname[1]


def log_dhcp_pool(filename, session):
    with open(filename, "w") as f:
        dhcp = session.send_command('show run | include ip dhcp pool')
        f.write(dhcp)


def modify_dhcp_pool(filename, session):
    with open(filename) as f:
        pool_list = f.readlines()

    logger.debug("\n** Entering (config) mode...")
    session.config_mode()

    for pool in pool_list:
        logger.debug("\n** Entering command: {}".format(pool.splitlines()))
        session.send_command("\n{}".format(pool))

        for dnsserv in dns_srv_list:
            logger.debug("** Entering command: dns-server {}".format(dnsserv.splitlines()))
            session.send_command("dns-server {}".format(dnsserv))

    logger.debug("\n** Exiting (config) mode...")
    session.exit_config_mode()


# Creates SSH Session and loops through each host
for host in host_list:
    ssh_session = ConnectHandler(device_type='cisco_ios', ip=host, username=UN, password=PW)
    hostname = get_hostname(show_cmd_list[0], ssh_session)

    # Create the Handler for logging data to a file
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('log_{}.log'.format(hostname))
    # set handler log levels
    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    # Add the Handlers to the Logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    dhcp_pool_name = 'dhcp_{}.txt'.format(hostname)
    log_dhcp_pool(dhcp_pool_name, ssh_session)

    logger.debug("\n****************************")
    logger.debug("HostName: {}".format(hostname))
    logger.debug("Host IP: {}".format(host))
    logger.debug("****************************")

    logger.debug('Logging is activated for {}\n'.format(hostname))

    # Loops through list of show commands on each host
    for cmd in show_cmd_list:
        logger.debug("\n** Entering command: {}".format(cmd.splitlines()))
        log = ssh_session.send_command(cmd)
        logger.debug("\n{}".format(log))

    # Modify dhcp dns-server in each pool
    modify_dhcp_pool(dhcp_pool_name, ssh_session)

    # Disconnects SSH session and proceeds to next host
    logger.debug("\n** Entering command: {}".format(show_cmd_list[1].splitlines()))
    output = ssh_session.send_command('show run | section ip dhcp pool')
    logger.debug("\n{}\n".format(output))

    logger.debug("\n** Entering command: {}".format("['write memory']"))
    output = ssh_session.send_command('write memory')
    logger.info("\n{}\n".format(output))

    logger.debug("** Disconnecting from: {} **\n".format(hostname))
    ssh_session.disconnect()

    logger.removeHandler(file_handler)
    logger.removeHandler(console_handler)
