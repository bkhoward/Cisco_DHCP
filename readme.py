# Cisco_DHCP
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
