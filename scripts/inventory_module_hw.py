#!/usr/bin/env python3
'''
Name: inventory_module_info.py
Summary: NXAPI: display model, hw, sw versions for ``--module``

Example output:

% ./inventory_module_hw.py --module 1 --devices cvd_leaf_1,cvd_leaf_2,cvd_spine_1,cvd_bgw_3
ip              hostname             module model                hw       sw      
192.168.11.102  cvd-1311-leaf        1      N9K-C93180YC-EX      2.0      10.2(3) 
192.168.11.103  cvd-1312-leaf        1      N9K-C93180YC-EX      2.0      10.2(3) 
192.168.11.112  cvd-1211-spine       1      N9K-X9732C-EX        1.4      10.2(3) 
192.168.11.100  cvd-2111-bgw         1      N9K-C9336C-FX2       1.0      10.2(3) 
% 

'''
our_version = 105
script_name = 'inventory_module_info'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_module_info import NxapiModuleInfo

def get_parser():
    help_module = 'module to query for hardware revision'
    ex_module = 'Example: --module 1'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display model, hw, sw versions for --module',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    mandatory.add_argument('--module',
                        dest='module',
                        required=True,
                        help='{} {}'.format(help_module, ex_module))

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
    print(fmt.format('ip', 'hostname', 'module', 'model', 'hw', 'sw'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiModuleInfo(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    try:
        nx.module = int(cfg.module)
    except:
        log.error('Early return. Expected integer for --module. Got {}'.format(cfg.module))
        return
    lines = list()
    lines.append(fmt.format(ip, nx.hostname, cfg.module, nx.model, nx.hw, nx.sw))
    return lines

fmt = '{:<15} {:<20} {:<6} {:<20} {:<8} {:<8}'

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
