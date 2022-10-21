#!/usr/bin/env python3
'''
Name: inventory_switch_serial_numbers.py
Description: NXAPI: display all serial numbers

Sample output

% ./inventory_switch_serial_numbers.py --vault hashicorp --devices cvd_leaf_1                  
ip              hostname           serial       name                 description
192.168.20.101  cvd-1311-leaf      FDO55550U5D  Chassis              Nexus9000 C93180YC-EX chassis
192.168.20.101  cvd-1311-leaf      FDO55550U5D  Slot 1               48x10/25G + 6x40/100G Ethernet Module
192.168.20.101  cvd-1311-leaf      LIT25555N5X  Power Supply 1       Nexus9000 C93180YC-EX chassis Power Supply
192.168.20.101  cvd-1311-leaf      LIT25555N7X  Power Supply 2       Nexus9000 C93180YC-EX chassis Power Supply
192.168.20.101  cvd-1311-leaf      N/A          Fan 1                Nexus9000 C93180YC-EX chassis Fan Module
192.168.20.101  cvd-1311-leaf      N/A          Fan 2                Nexus9000 C93180YC-EX chassis Fan Module
192.168.20.101  cvd-1311-leaf      N/A          Fan 3                Nexus9000 C93180YC-EX chassis Fan Module
192.168.20.101  cvd-1311-leaf      N/A          Fan 4                Nexus9000 C93180YC-EX chassis Fan Module
% 

'''
our_version = 110
script_name = 'serial_numbers'

#standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_inventory import NxapiInventory


def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display all serial numbers.',
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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)
        if len(output) > 0:
            print()

def print_header():
    print(fmt.format('ip', 'hostname', 'serial', 'name', 'description'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInventory(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    for item in nx.info:
        lines.append(fmt.format(
            ip,
            nx.hostname, 
            nx.info[item]['serialnum'],
            nx.info[item]['name'],
            nx.info[item]['desc']))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<12} {:<20} {:<25}'
print_header()
executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
