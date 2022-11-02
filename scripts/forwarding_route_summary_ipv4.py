#!/usr/bin/env python3
our_version = 106
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
from concurrent.futures import ThreadPoolExecutor
#local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.general.verify_types import Constants
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_forwarding_route_summary import NxapiForwardingRouteSummaryIpv4

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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def get_header():
    return fmt.format('IP', 'Hostname', 'Value', 'Description')

def collect_output(ip, fib):
    lines = list()
    lines.append(get_header())
    lines.append(fmt.format(ip, fib.hostname, fib.route_count,   'FIBv4 routes'))
    lines.append(fmt.format(ip, fib.hostname, fib.path_count,    'FIBv4 paths'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_updates, 'Route updates'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_inserts, 'Route inserts'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_deletes, 'Route deletes'))
    for prefixlen in range(0, c.ipv4_mask_length + 1):
        fib.mask_length = prefixlen
        if fib.mask_length == -1:
            continue
        lines.append('{:<15} {:<20} {:>9} /{:<3} {:<9}'.format(ip, fib.hostname, fib.mask_length, prefixlen, 'prefixlen'))
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiForwardingRouteSummaryIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vrf = cfg.vrf
    nx.module = cfg.module
    nx.refresh()
    return collect_output(ip, nx)

fmt = '{:<15} {:<20} {:>9} {:<14}'
c = Constants() # see collect_output()
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
