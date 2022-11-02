#!/usr/bin/env python3
'''
Name: interface_link_not_connected.py
Description: NXAPI: display interfaces with state "Link not connected"

Example:

NOTE: cvd_spine_1 produces no output since it has no interfaces in notconnect state.

(% ./interface_link_not_connected.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_spine_1
ip              hostname             interface          state                speed xcvr                
192.168.11.102  cvd-1311-leaf        Ethernet1/9        notconnect           auto  SFP-H25GB-CU5M      
192.168.11.102  cvd-1311-leaf        Ethernet1/11       notconnect           auto  SFP-H10GB-AOC2M     
192.168.11.102  cvd-1311-leaf        Ethernet1/12       notconnect           auto  SFP-H10GB-AOC2M     

192.168.11.103  cvd-1312-leaf        Ethernet1/9        notconnect           auto  SFP-H25GB-CU5M      
192.168.11.103  cvd-1312-leaf        Ethernet1/11       notconnect           auto  SFP-H10GB-AOC2M     
192.168.11.103  cvd-1312-leaf        Ethernet1/12       notconnect           auto  SFP-H10GB-AOC2M     

% 
'''
our_version = 101
script_name = 'interface_link_not_connected.py'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_interface import NxapiInterface, NxapiInterfaceStatus

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display interfaces with state "Link not connected"',
        parents=[ArgsCookie, ArgsNxapiTools])
    optional = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

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
    print(fmt.format('ip', 'hostname', 'interface', 'state', 'speed', 'xcvr'))

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)
        if len(output) > 0:
            print()

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    s = NxapiInterfaceStatus(vault.nxos_username, vault.nxos_password, ip, log)
    s.nxapi_init(cfg)
    s.refresh()
    # we're using NxapiInterface only for the is_virtual_interface method
    # so we don't need to call nxapi_init() on it.
    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    lines = list()
    for interface in s.info:
        if i.is_virtual_interface(interface):
            continue
        s.interface = interface
        if s.state != 'notconnect':
            continue
        lines.append(fmt.format(ip, s.hostname, s.interface, s.state, s.speed, s.type))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<20} {:<18} {:<20} {:<5} {:<20}'
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
