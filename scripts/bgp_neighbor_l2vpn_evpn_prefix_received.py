#!/usr/bin/env python3
'''
Name: bgp_neighbor_l2vpn_evpn_prefix_received.py
Description: NXAPI: display bgp l2vpn evpn summary info
'''
our_version = 102
script_name = 'bgp_neighbor_l2vpn_evpn_prefix_received'
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
from nxapi.nxapi_bgp_l2vpn_evpn_summary import NxapiBgpL2vpnEvpnSummary

def get_parser():
    help_nonzero = 'if specified, only display neighbors with non-zero prefixes received'
    ex_prefix = 'Example: '
    ex_nonzero = '{} --nonzero'.format(ex_prefix)

    parser = argparse.ArgumentParser(description='DESCRIPTION: NXAPI: display bgp l2vpn evpn summary info', parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

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
    print(fmt.format('ip', 'hostname', 'l2vpn_evpn_neighbor', 'prefix_rx'))

def collect_prefix_rx(ip, bgp):
    lines = list()
    for neighbor in bgp.neighbor_info:
        bgp.neighbor = neighbor
        try:
            prefixreceived = int(bgp.prefixreceived)
        except:
            log.error('exiting. cannot convert bgp.prefixreceived {} to int()'.format(bgp.prefixreceived))
            exit(1)
        if prefixreceived == 0 and cfg.nonzero == True:
            continue
        lines.append(fmt.format(ip, bgp.hostname, bgp.neighbor, bgp.prefixreceived))
    output[ip] = lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiBgpL2vpnEvpnSummary(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    i.vrf = cfg.vrf
    i.refresh()
    collect_prefix_rx(ip, i)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)
# keyed on ip address, value is a list containing the worker's output
output = dict()

devices = get_device_list()

fmt = '{:<15} {:<20} {:<19} {:>9}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join(timeout=5)
for ip in sorted(output):
    for line in output[ip]:
        print('{}'.format(line))
    print()
