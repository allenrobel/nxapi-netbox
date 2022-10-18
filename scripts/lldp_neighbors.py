#!/usr/bin/env python3
'''
Name: lldp_neighbors.py
Description: NXAPI: display lldp neighbor info for one or more NX-OS switches

Example usage:

./lldp_neighbors --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2

Example output:

% ./lldp_neighbors.py --vault hashicorp --devices cvd_leaf_1 
local_name       local_port nbr_name         nbr_port      nbr_mgmt_address
cvd-1311-leaf    mgmt0      mgmt_vlan_150    Ethernet1/47  acf2.c506.bd96 
cvd-1311-leaf    Eth1/11    cvd_911_fanout   Ethernet1/1   172.22.150.116 
cvd-1311-leaf    Eth1/12    cvd_911_fanout   Ethernet1/2   172.22.150.116 
cvd-1311-leaf    Eth1/49    cvd-1211-spine   Ethernet1/1   172.22.150.112 
cvd-1311-leaf    Eth1/50    cvd-1211-spine   Ethernet2/1   172.22.150.112 
cvd-1311-leaf    Eth1/51    cvd-1212-spine   Ethernet1/1   172.22.150.113 
cvd-1311-leaf    Eth1/52    cvd-1212-spine   Ethernet2/1   172.22.150.113 
% 

'''
our_version = 105
script_name = 'lldp_neighbors'

# standard libraries
import argparse
from threading import Thread, Lock
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_lldp import NxapiLldpNeighbors

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display lldp neighbor info for one or more NX-OS switches.',
        parents=[ArgsCookie, ArgsNxapiTools])

    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    parser.add_argument('--version',
                        action='version', 
                        version='{} v{}'.format('%(prog)s', our_version))
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)

def print_header():
    print(fmt.format('local_name', 'local_port', 'nbr_name', 'nbr_port', 'nbr_mgmt_address'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    lldp = NxapiLldpNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    lldp.nxapi_init(cfg)
    lldp.refresh()
    with lock:
        for local_port in lldp.info:
            print(fmt.format(
                lldp.hostname,
                local_port,
                lldp.info[local_port]['chassis_id'],
                lldp.info[local_port]['port_id'],
                lldp.info[local_port]['mgmt_addr']))

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<16} {:<10} {:<16} {:<13} {:<15}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
