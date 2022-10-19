#!/usr/bin/env python3
our_version = 108
script_name = 'switch_version'
'''
Name: switch_version.py
Description: NXAPI: display NXOS version information

Example usage:

./switch_version.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2
'''
# standard libraries
import argparse
from threading import Thread, Lock
from time import sleep
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
        description='DESCRIPTION: NXAPI: display NXOS version information',
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
    print(fmt.format('ip', 'hostname', 'bios', 'nxos_version'))

def print_info(ip, output):
    print(fmt.format(
        ip,
        output[ip].hostname,
        output[ip].bios_ver_str,
        output[ip].nxos_ver_str))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiVersion(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    output[ip] = nx

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

output = dict()

fmt = '{:<15} {:<20} {:<9} {:<32}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()
for ip in sorted(output):
    print_info(ip, output)
