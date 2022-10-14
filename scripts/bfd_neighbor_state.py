#!/usr/bin/env python3
'''
Name: bfd_neighbor_state.py
Description: display bfd neighbor state for all neighbors

Example:

watch ./bfd_neighbor_state.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2
'''
our_version = 104
script_name = 'bfd_neighbor_state'

# standard libraries
import argparse
#from time import sleep
from threading import Thread, Lock

# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_bfd import NxapiBfdNeighbors

def get_parser():
    title = 'display bfd neighbor state for all neighbors on --device'
    parser = argparse.ArgumentParser(description='DESCRIPTION: {}'.format(title), parents=[ArgsCookie, ArgsNxapiTools])
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

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

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bfd = NxapiBfdNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    bfd.nxapi_init(cfg)

    bfd.refresh()
    with lock:
        print(fmt.format(
            'DUT',
            'local_disc',
            'local_port',
            'src_ip_addr',
            'dest_ip_addr',
            'local_state',
            'remote_state'))
        for local_disc in bfd.info:
            bfd.local_disc = local_disc
            print(fmt.format(
                bfd.hostname,
                local_disc,
                bfd.intf,
                bfd.src_ip_addr,
                bfd.dest_ip_addr,
                bfd.local_state,
                bfd.remote_state))
        print('')

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

fmt = '{:<15} {:<10} {:<15} {:<13} {:<13} {:<12} {:<12}'

devices = get_device_list()
# if len(devices) > 1:
#     log.error('exiting. Unlike most scripts in this repo, this script supports only one device.')
#     exit(1)

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
