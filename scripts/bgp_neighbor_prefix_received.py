#!/usr/bin/env python3
'''
Name: bgp_neighbor_prefix_received.py
Description: NXAPI: display bgp neighbor summary info
'''
our_version = 107
script_name = 'bgp_neighbor_prefix_received'
# standard libraries
import argparse
from threading import Thread, active_count
from time import sleep

# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_bgp_unicast_summary import NxapiBgpUnicastSummaryIpv4, NxapiBgpUnicastSummaryIpv6

def get_parser():
    help_afi = 'address family to query. one of ipv4 or ipv6 or all. If all is selected, then all address families are displayed'
    help_nonzero = 'if specified, only display neighbors with non-zero prefixes received'
    ex_prefix = 'Example: '
    ex_afi = '{} --afi ipv6'.format(ex_prefix)
    ex_nonzero = '{} --nonzero'.format(ex_prefix)

    parser = argparse.ArgumentParser(description='DESCRIPTION: display bgp unicast summary info via NXAPI', parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--afi',
                           dest='afi',
                           required=False,
                           choices=['ipv4', 'ipv6'],
                           default='ipv4',
                           help='{} {}'.format(help_afi, ex_afi))

    default.add_argument('--nonzero',
                           dest='nonzero',
                           required=False,
                           default=False,
                           action='store_true',
                           help='{} {}'.format(help_nonzero, ex_nonzero))

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
    print(fmt.format('ip', 'hostname', 'neighbor', 'prefix_rx'))

def collect_prefix_rx(ip, bgp):
    lines = list()
    for neighbor in bgp.neighbor_info:
        bgp.neighbor = neighbor
        try:
            prefixreceived = int(bgp.prefixreceived)
        except:
            log.warning('collect_prefix_rx. {} skipping neighbor {}. cannot convert bgp.prefixreceived {} to int()'.format(
                bgp.hostname,
                bgp.neighbor,
                bgp.prefixreceived))
            continue
        if prefixreceived == 0 and cfg.nonzero == True:
            continue
        lines.append(fmt.format(ip, bgp.hostname, bgp.neighbor, bgp.prefixreceived))
    output[ip] = lines

def get_instance(ip, vault):
    '''
    return a list of NxapiBgpUnicastSummary*() instances based on cfg.afi
    '''
    if cfg.afi == 'ipv4':
        return NxapiBgpUnicastSummaryIpv4(vault.nxos_username,vault.nxos_password,ip,log)
    elif cfg.afi == 'ipv6':
        return NxapiBgpUnicastSummaryIpv6(vault.nxos_username,vault.nxos_password,ip,log)
    else:
        log.error('exiting. Unknown afi {}'.format(cfg.afi))
        exit(1)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    instance = get_instance(ip, vault)
    instance.nxapi_init(cfg)
    instance.vrf = cfg.vrf
    instance.refresh()
    collect_prefix_rx(ip, instance)

def get_fmt():
    fmt_ipv6 = '{:<15} {:<18} {:<40} {:>9}'
    fmt_ipv4 = '{:<15} {:<18} {:<15} {:>9}'
    if cfg.afi == 'ipv4':
        return fmt_ipv4
    else:
        return fmt_ipv6

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)
# keyed on ip address, value is a list containing the worker's output
output = dict()

devices = get_device_list()

fmt = get_fmt()
print_header()

for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join(timeout=5)
for sid in sorted(output):
    for line in output[sid]:
        print('{}'.format(line))
    print()
