#!/usr/bin/env python3
'''
Name: bgp_neighbors.py
Description: NXAPI: display detailed bgp neighbor information

Synopsis:

./bgp_neighbors_format_table.py --vault hashicorp --devices cvd_leaf_1
'''

our_version = 104
script_name = 'bgp_neighbors_format_table'

# standard libraries
import argparse
from threading import Thread, Lock

# local libraries
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_bgp_neighbors import NxapiBgpNeighborsIpv4

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display detailed bgp neighbor information.',
        parents=[ArgsCookie,ArgsNxapiTools])
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
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

def get_max_key_length(d):
    #log.info('d {}'.format(d))
    length = 0
    for peer in d:
        for key in d[peer]:
            if len(str(key)) > length:
                length = len(str(key))
            if type(d[peer][key]) != type(dict()):
                continue
            for k in d[peer][key]:
                if len(str(k)) > length:
                    length = len(str(k))
    return length

def print_header(d):
    key_length = get_max_key_length(d)
    print('{:<15} {:<15} {:<{length}} {}'.format('dut', 'peer', 'key', 'value', length=key_length))

def print_dict(d, hostname):
    key_length = get_max_key_length(d)
    for peer in d:
        for key in sorted(d[peer]):
            value = d[peer][key]
            if type(value) != type(dict()):
                print("{:<15} {:<15} {:<{length}} {}".format(hostname, peer, key, value, length=key_length))
                continue
            for k in value:
                print("{:<15} {:<15} {:<{length}} {}".format(hostname, peer, k, value[k], length=key_length))
        print()

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bgp = NxapiBgpNeighborsIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    bgp.nxapi_init(cfg)
    bgp.refresh()
    with lock:
        print()
        print_header(bgp.peer_global)
        print_dict(bgp.peer_global, bgp.hostname)

        print_header(bgp.capextendednhaf)
        print_dict(bgp.capextendednhaf, bgp.hostname)

        print_header(bgp.capextendednhsaf)
        print_dict(bgp.capextendednhsaf, bgp.hostname)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

lock = Lock()
devices = get_device_list()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
