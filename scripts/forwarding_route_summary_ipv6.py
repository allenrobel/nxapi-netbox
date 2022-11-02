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
our_version = 106
script_name = 'forwarding_route_summary_ipv6'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
#local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.general.constants import Constants
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_forwarding_route_summary import NxapiForwardingRouteSummaryIpv6

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
    lines.append(fmt.format(ip, fib.hostname, fib.route_count,   'FIBv6 routes'))
    lines.append(fmt.format(ip, fib.hostname, fib.path_count,    'FIBv6 paths'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_updates, 'Route updates'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_inserts, 'Route inserts'))
    lines.append(fmt.format(ip, fib.hostname, fib.route_deletes, 'Route deletes'))
    for prefixlen in range(0, c.ipv6_mask_length + 1):
        fib.mask_length = prefixlen
        if fib.mask_length == -1:
            continue
        lines.append('{:<15} {:<20} {:>9} /{:<3} {:<9}'.format(ip, fib.hostname, fib.mask_length, prefixlen, 'prefixlen'))
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiForwardingRouteSummaryIpv6(vault.nxos_username, vault.nxos_password, ip, log)
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
