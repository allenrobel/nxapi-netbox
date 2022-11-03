#!/usr/bin/env python3
'''
Name: system_mode.py
Description: NXAPI: display system mode

Example output:

% ./system_mode.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2
ip              hostname           system_mode timer_state              
172.22.150.102  cvd-1311-leaf      Normal      na                       
172.22.150.103  cvd-1312-leaf      Maintenance switch to maintenance mode in progress
%
'''
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_system_mode import NxapiSystemMode

our_version = 102
script_name = 'system_mode'

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display system mode',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def print_header():
    print(fmt.format('ip', 'hostname', 'system_mode', 'timer_state'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiSystemMode(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    lines.append(fmt.format(ip, nx.hostname, nx.system_mode, nx.timer_state))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<11} {:<25}'
print_header()
executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
