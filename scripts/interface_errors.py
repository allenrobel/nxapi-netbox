#!/usr/bin/env python3
'''
Name: interface_errors.py
Summary: NXAPI: display non-zero interface error counters

Synopsis:

./nxapi_interface_errors_sid.py --vault hashicorp --devices leaf_1,leaf_2
'''
our_version = 103
script_name = 'interface_errors'

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
from nxapi.nxapi_interface import NxapiInterfaceAll

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

def print_header():
    print(fmt.format('ip', 'hostname', 'interface', 'value', 'type'))

def print_info(ip, i):
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
            print(fmt.format(ip, i.hostname, i.interface, errors[error], error))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInterfaceAll(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    result = i.refresh()
    if not result:
        return
    with lock:
        print_info(ip, i)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<15} {:>11} {:<15}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
