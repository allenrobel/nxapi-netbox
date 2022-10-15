#!/usr/bin/env python3
'''
Name: nxapi_forwarding_route_summary_ipv6.py
Description: NXAPI: display forwarding ipv6 route summary

Example usage

When no ipv6 routes are present, you'll see some warnings regarding module and vrf tables not being present, and all values will be -1, per below.

% ./forwarding_route_summary_ipv6.py --vault hashicorp --devices cvd_leaf_1
2022-10-14 16:19:59,630 WARNING 5545.81 nxapi_base._get_table_row cvd-1311-leaf early return: [TABLE_module][ROW_module] not present in _json {}
2022-10-14 16:19:59,630 WARNING 5545.81 nxapi_base._get_table_row cvd-1311-leaf early return: [TABLE_vrf][ROW_vrf] not present in _json {}
IP              Hostname                 Value Description   
192.168.11.101  cvd-1311-leaf               -1 FIBv6 routes  
192.168.11.101  cvd-1311-leaf               -1 FIBv6 paths   
192.168.11.101  cvd-1311-leaf               -1 Route updates 
192.168.11.101  cvd-1311-leaf               -1 Route inserts 
192.168.11.101  cvd-1311-leaf               -1 Route deletes 
% 

If we add one route (here, a static route to null0), the warnings are no longer printed, since the tables are now present.

ipv6 route 2011::1/128 Null0

% ./forwarding_route_summary_ipv6.py --vault hashicorp --devices cvd_leaf_1
IP              Hostname                 Value Description   
192.168.11.101  cvd-1311-leaf                4 FIBv6 routes  
192.168.11.101  cvd-1311-leaf                4 FIBv6 paths   
192.168.11.101  cvd-1311-leaf               -1 Route updates 
192.168.11.101  cvd-1311-leaf               -1 Route inserts 
192.168.11.101  cvd-1311-leaf               -1 Route deletes 
192.168.11.101  cvd-1311-leaf                1 /8   prefixlen
192.168.11.101  cvd-1311-leaf                1 /10  prefixlen
192.168.11.101  cvd-1311-leaf                1 /127 prefixlen
192.168.11.101  cvd-1311-leaf                1 /128 prefixlen
%
'''
our_version = 104
script_name = 'forwarding_route_summary_ipv6'

# standard libraries
import argparse
from threading import Thread, Lock
#local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from general.constants import Constants
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_forwarding_route_summary import NxapiForwardingRouteSummaryIpv6

def get_parser():
    help_module = 'module on which to query forwarding ipv6 route summary info'
    ex_module = ' Example: --module 2'
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: Display forwarding ipv6 route summary via NXAPI',
        parents=[ArgsCookie,ArgsNxapiTools])
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    optional.add_argument('--module',
                        dest='module',
                        required=False,
                        default=1,
                        help='{} {}'.format(help_module, ex_module))

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
    print(fmt.format('IP', 'Hostname', 'Value', 'Description'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    fib = NxapiForwardingRouteSummaryIpv6(vault.nxos_username, vault.nxos_password, ip, log)
    fib.nxapi_init(cfg)
    fib.vrf = cfg.vrf
    fib.module = cfg.module
    fib.refresh()
    with lock:
        print_header()
        print(fmt.format(ip, fib.hostname, fib.route_count,   'FIBv6 routes'))
        print(fmt.format(ip, fib.hostname, fib.path_count,    'FIBv6 paths'))
        print(fmt.format(ip, fib.hostname, fib.route_updates, 'Route updates'))
        print(fmt.format(ip, fib.hostname, fib.route_inserts, 'Route inserts'))
        print(fmt.format(ip, fib.hostname, fib.route_deletes, 'Route deletes'))
        for prefixlen in range(0, c.ipv6_mask_length + 1):
            fib.mask_length = prefixlen
            if fib.mask_length == -1:
                continue
            print('{:<15} {:<20} {:>9} /{:<3} {:<9}'.format(ip, fib.hostname, fib.mask_length, prefixlen, 'prefixlen'))

fmt = '{:<15} {:<20} {:>9} {:<14}'

c = Constants() # worker()
cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()
