#!/usr/bin/env python3
'''
Name: license_hostid.py
Description: NXAPI: display license host_id for one or more NX-OS switches

Example usage:

% ./license_hostid.py --vault hashicorp --devices cvd_leaf_1,cvd_spine_1
ip              hostname           hostid        
192.168.11.105  cvd-1211-spine     FOX1304PBXS    
192.168.11.101  cvd-1311-leaf      FDO65050U5M    
 % 
'''
our_version = 106
script_name = 'license_hostid'

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
from nxapi.nxapi_license_hostid import NxapiLicenseHostid

def get_parser():
    parser = argparse.ArgumentParser(
        description='NXAPI: display license host_id for one or more NX-OS switches.',
            parents=[ArgsCookie, ArgsNxapiTools])

    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    optional = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')

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
    print(fmt.format('ip', 'hostname', 'hostid'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    n = NxapiLicenseHostid(vault.nxos_username, vault.nxos_password, ip, log)
    n.nxapi_init(cfg)
    n.refresh()
    with lock:
        print(fmt.format(ip, n.hostname, n.host_id))

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<15}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
