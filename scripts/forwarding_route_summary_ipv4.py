#!/usr/bin/env python3
our_version = 104
'''
Name: forwarding_route_summary_ipv4.py
Description: NXAPI: display forwarding ipv4 route summary

Example usage

% ./forwarding_route_summary_ipv4.py --vault hashicorp --devices cvd_leaf_1
IP              Hostname                 Value Description   
192.168.11.101  cvd-1311-leaf               83 FIBv4 routes  
192.168.11.101  cvd-1311-leaf              140 FIBv4 paths   
192.168.11.101  cvd-1311-leaf              106 Route updates 
192.168.11.101  cvd-1311-leaf              263 Route inserts 
192.168.11.101  cvd-1311-leaf               22 Route deletes 
192.168.11.101  cvd-1311-leaf                1 /8   prefixlen
192.168.11.101  cvd-1311-leaf               47 /30  prefixlen
192.168.11.101  cvd-1311-leaf               35 /32  prefixlen

'''
script_name = 'forwarding_route_summary_ipv4'

# standard libraries
import argparse
from threading import Thread, Lock
#local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from general.verify_types import Constants
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_forwarding_route_summary import NxapiForwardingRouteSummaryIpv4

def get_parser():
    help_module = 'module on which to query forwarding ipv4 route summary info'
    ex_module = ' Example: --module 2'
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display forwarding ipv4 route summary',
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
    fib = NxapiForwardingRouteSummaryIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    fib.nxapi_init(cfg)
    fib.vrf = cfg.vrf
    fib.module = cfg.module
    fib.refresh()
    with lock:
        print_header()
        print(fmt.format(ip, fib.hostname, fib.route_count,   'FIBv4 routes'))
        print(fmt.format(ip, fib.hostname, fib.path_count,    'FIBv4 paths'))
        print(fmt.format(ip, fib.hostname, fib.route_updates, 'Route updates'))
        print(fmt.format(ip, fib.hostname, fib.route_inserts, 'Route inserts'))
        print(fmt.format(ip, fib.hostname, fib.route_deletes, 'Route deletes'))
        for prefixlen in range(0, c.ipv4_mask_length + 1):
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
