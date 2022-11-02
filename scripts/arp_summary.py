#!/usr/bin/env python3
'''
Name: arp_summary.py
Description: NXAPI: display ip arp summary 
Dependencies: See README.md in this directory
'''
our_version = 101
script_name = 'arp_summary'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_arp import NxapiArpSummary

def get_parser():
    parser = argparse.ArgumentParser(description='DESCRIPTION: NXAPI: display ip arp summary', parents=[ArgsCookie, ArgsNxapiTools])
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
    print(fmt.format(
        'ipv4',
        'dut',
        'vrf',
        'resolved',
        'incomplete',
        'throttled',
        'unknown',
        'total'))

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    arp = NxapiArpSummary(vault.nxos_username, vault.nxos_password, ip, log)
    arp.nxapi_init(cfg)
    arp.vrf = cfg.vrf
    arp.refresh()
    lines = list()
    lines.append(fmt.format(
        ip,
        arp.hostname,
        arp.vrf,
        arp.resolved,
        arp.incomplete,
        arp.throttled,
        arp.unknown,
        arp.total))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<14} {:>10} {:>13} {:>15} {:>15} {:>12} {:>12}'
print_header()
executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
