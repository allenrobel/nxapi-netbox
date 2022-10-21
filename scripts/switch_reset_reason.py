#!/usr/bin/env python3
our_version = 102
script_name = 'switch_reset_reason'
'''
Name: switch_reset_reason.py
Description: NXAPI: display NXOS reset reason

Example output:

% ./switch_reset_reason.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_leaf_3,cvd_leaf_4,cvd_spine_1,cvd_spine_2
ip              hostname           version              ctime                     reason                          
192.168.11.102  cvd-1311-leaf      10.2(3)              Mon Oct 17 23:45:55 2022  Reset Requested by CLI command reload
192.168.11.103  cvd-1312-leaf      10.2(3)              Mon Oct 17 23:55:04 2022  Reset Requested by CLI command reload
192.168.11.104  cvd-1313-leaf      10.2(3)              Tue Oct 18 00:04:02 2022  Reset Requested by CLI command reload
192.168.11.105  cvd-1314-leaf      10.2(3)              Tue Oct 18 00:14:49 2022  Reset Requested by CLI command reload
192.168.11.112  cvd-1211-spine     10.2(3)              Tue Oct 18 02:21:21 2022  Reset Requested by CLI command reload
192.168.11.113  cvd-1212-spine     10.2(3)              Tue Oct 18 02:37:54 2022  Reset Requested by CLI command reload
% 
'''
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_version import NxapiVersion

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display NXOS reset reason',
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
    print(fmt.format('ip', 'hostname', 'version', 'ctime', 'reason'))

def get_output(ip, nx):
    return fmt.format(
        ip,
        nx.hostname,
        nx.rr_sys_ver,
        nx.rr_ctime,
        nx.rr_reason)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiVersion(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    lines.append(get_output(ip, nx))
    return lines

fmt = '{:<15} {:<18} {:<20} {:<25} {:<32}'

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
