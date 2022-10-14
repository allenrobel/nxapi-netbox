#!/usr/bin/env python3

script_name = 'inventory'
our_version = 100
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
from nxapi.nxapi_inventory import NxapiInventory

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display inventory info',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
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
    print(fmt.format('ip', 'hostname', 'serial', 'name', 'product_id', 'description'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInventory(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init()
    # if argparse is used, pass argparse instance to nxapi_init for control
    # over urllib3 configuration and cookie behavior
    i.nxapi_init(cfg)
    i.refresh()
    d = i.info
    with lock:
        for item in d:
            i.item = item
            print(fmt.format(
                ip,
                i.hostname,
                i.serialnum,
                i.name,
                i.productid,
                i.desc))
        print()


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<12} {:<15} {:<18} {:<30}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
