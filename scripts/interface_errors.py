#!/usr/bin/env python3
'''
Name: interface_errors.py
Summary: NXAPI: display non-zero interface error counters

Example output:

% ./interface_errors.py --vault hashicorp --devices cvd_l2_fanout,cvd_leaf_1                                              
ip              hostname           interface             value type           
192.168.11.116  cvd_l2_911         Ethernet1/17           9821 eth_inerr      
192.168.11.116  cvd_l2_911         Ethernet1/17           9820 eth_crc        

% 
'''
our_version = 105
script_name = 'interface_errors'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_interface import NxapiInterfaceAll

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display non-zero interface error counters',
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
    print(fmt.format('ip', 'hostname', 'interface', 'value', 'type'))

def collect_info(ip, i):
    lines = list()
    for interface in i.interface_list:
        i.interface = interface
        errors = i.errors
        for error in errors:
            # 'na' is returned for some errors if interface does not support that error type
            if type(errors[error]) == type(str()):
                continue
            # skip zero and -1 values
            if errors[error] <= 0:
                continue
            lines.append(fmt.format(ip, i.hostname, i.interface, errors[error], error))
    if len(lines) != 0:
        lines.append('')
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInterfaceAll(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    result = i.refresh()
    if not result:
        return
    return collect_info(ip, i)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
fmt = '{:<15} {:<18} {:<15} {:>11} {:<15}'
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
