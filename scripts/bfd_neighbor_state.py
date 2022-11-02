#!/usr/bin/env python3
'''
Name: bfd_neighbor_state.py
Description: display bfd neighbor state for all neighbors

Example:

watch ./bfd_neighbor_state.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2
'''
our_version = 106
script_name = 'bfd_neighbor_state'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
from gc import collect

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_bfd import NxapiBfdNeighbors

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

def print_header():
    print(fmt.format(
        'DUT',
        'local_disc',
        'local_port',
        'src_ip_addr',
        'dest_ip_addr',
        'local_state',
        'remote_state'))

def collect_info(ip, bfd):
    lines = list()
    for local_disc in bfd.info:
        bfd.local_disc = local_disc
        lines.append(fmt.format(
            bfd.hostname,
            local_disc,
            bfd.intf,
            bfd.src_ip_addr,
            bfd.dest_ip_addr,
            bfd.local_state,
            bfd.remote_state))
    lines.append('')
    return lines

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bfd = NxapiBfdNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    bfd.nxapi_init(cfg)
    bfd.refresh()
    lines = collect_info(ip, bfd)
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

fmt = '{:<15} {:<10} {:<15} {:<13} {:<13} {:<12} {:<12}'

devices = get_device_list()

print_header()
executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
