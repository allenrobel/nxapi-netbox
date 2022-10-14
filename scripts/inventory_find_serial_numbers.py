#!/usr/bin/env python3
'''
Name: inventory_find_serial_numbers.py
Description: NXAPI: find one or more serial numbers across a set of NXOS switches
'''
our_version = 110
script_name = 'inventory_find_serial_numbers'

#standard libraries
import argparse
from threading import Thread, Lock
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_inventory import NxapiInventory

def get_parser():
    help_serials = 'a comma-separated list (no spaces) of Nexus serial numbers'
    ex_prefix = 'Example:'
    ex_serials = '{} --serials SAL2232U92Z,FOC321617XA,FOC631317XA'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: find one or more serial numbers across a set of NXOS switches.',
        parents=[ArgsCookie, ArgsNxapiTools])

    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    mandatory.add_argument('--serials',
                        dest='serials',
                        required=True,
                        help='(default: %(default)s) ' + help_serials + ex_serials,
                        )

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + str(our_version))
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)
def get_serial_number_list():
    try:
        return cfg.serials.split(',')
    except:
        log.error('exiting. Cannot parse --serials {}.  Example usage: --serials SAL2232U92Z,FOC321617XA,FOC631317XA'.format(cfg.serials))
        exit(1)

def print_header():
    print(fmt.format(
        'ip',
        'hostname',
        'serial',
        'name',
        'product_id',
        'description'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInventory(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    i.refresh()
    d = i.info
    with lock:
        for item in d:
            i.item = item
            if i.serialnum not in serial_numbers:
                continue
            print(fmt.format(
                ip,
                i.hostname,
                i.serialnum,
                i.name,
                i.productid,
                i.desc))

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
serial_numbers = get_serial_number_list()

fmt = '{:<15} {:<20} {:<12} {:<15} {:<16} {:<30}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()

