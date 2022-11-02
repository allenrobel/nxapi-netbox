#!/usr/bin/env python3
'''
Name: bgp_neighbors.py
Description: NXAPI: display detailed bgp neighbor information

Usage:

./bgp_neighbors.py --vault hashicorp --devices cvd_leaf_1
'''

our_version = 106
script_name = 'bgp_neighbors'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_bgp_neighbors import NxapiBgpNeighborsIpv4

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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def get_max_key_length(d):
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

def get_header(d):
    key_length = get_max_key_length(d)
    return '{:<15} {:<15} {:<{length}} {}'.format('dut', 'peer', 'key', 'value', length=key_length)

def collect_output(d, hostname):
    key_length = get_max_key_length(d)
    lines = list()
    for peer in d:
        for key in sorted(d[peer]):
            value = d[peer][key]
            if type(value) != type(dict()):
                lines.append("{:<15} {:<15} {:<{length}} {}".format(hostname, peer, key, value, length=key_length))
                continue
            for k in value:
                lines.append("{:<15} {:<15} {:<{length}} {}".format(hostname, peer, k, value[k], length=key_length))
        lines.append('')
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bgp = NxapiBgpNeighborsIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    bgp.nxapi_init(cfg)
    bgp.refresh()
    lines = list()
    lines.append('')

    lines.append(get_header(bgp.peer_global))
    for line in collect_output(bgp.peer_global, bgp.hostname):
        lines.append(line)

    lines.append(get_header(bgp.capextendednhaf))
    for line in collect_output(bgp.capextendednhaf, bgp.hostname):
        lines.append(line)

    lines.append(get_header(bgp.capextendednhsaf))
    for line in collect_output(bgp.capextendednhsaf, bgp.hostname):
        lines.append(line)
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
