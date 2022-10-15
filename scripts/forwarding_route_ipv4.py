#!/usr/bin/env python3
our_version = 106
'''
Name: forwarding_route_ipv4.py
Description: NXAPI: Display ipv4 prefix information from FIB related to --module --vrf --prefix 

Example usage

Query an ipv4 prefix in an RFC5549 environment.

% ./forwarding_route_ipv4.py --vault hashicorp --devices cvd_leaf_1 --module 2 --prefix 10.239.0.24/32
hostname leaf_1 prefix 10.239.0.24/32 num_paths 4
  next_hop 2112:232::20     -> Ethernet1/3         
  next_hop 2112:232::22     -> Ethernet1/4         
  next_hop 2112:232::24     -> Ethernet2/3         
  next_hop 2112:232::26     -> Ethernet2/4         
%

Tracing a prefix across multiple devices.

% ./forwarding_route_ipv4.py --vault hashicorp --devices cvd_leaf_1,cvd_spine_1,cvd_leaf_3 --module 1 --prefix 10.2.0.3/32
hostname cvd-1311-leaf prefix 10.2.0.3/32 num_paths 4
  next_hop 10.4.0.2         -> Ethernet1/49        
  next_hop 10.4.0.18        -> Ethernet1/50        
  next_hop 10.4.0.46        -> Ethernet1/51        
  next_hop 10.4.0.50        -> Ethernet1/52        
hostname cvd-1211-spine prefix 10.2.0.3/32 num_paths 2
  next_hop 10.4.0.9         -> Ethernet1/3         
  next_hop 10.4.0.25        -> Ethernet2/3         
hostname cvd-1313-leaf prefix 10.2.0.3/32 num_paths 1
  next_hop Receive          -> sup-eth1            
%

'''
script_name = 'forwarding_route_ipv4'

# standard libraries
import argparse
from threading import Thread, Lock
from tty import CFLAG

#DSSPERF libraries
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from general.verify_types import VerifyTypes
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_forwarding_route_unicast import NxapiForwardingRouteUnicastIpv4

def get_parser():
    help_module = 'module to query for prefix'
    help_prefix = 'prefix to query'
    ex_pfx     = 'Example: '
    ex_module = '{} --module 2'.format(ex_pfx)
    ex_prefix = '{} --prefix 10.160.0.0/16'.format(ex_pfx)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: Display ipv4 prefix information from FIB related to --module --vrf --prefix',
        parents=[ArgsCookie,ArgsNxapiTools])

    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    optional = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')

    mandatory.add_argument('--module',
                        dest='module',
                        required=True,
                        help=help_module + ex_module)

    mandatory.add_argument('--prefix',
                        dest='prefix',
                        required=True,
                        help=help_module + ex_module)

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

def print_path_ip_nexthop(path):
    if 'ifname' not in path:
        return
    print('  next_hop {:<16} -> {:<20}'.format(path['ip_nexthop'], path['ifname']))
def print_path_special(path):
    if 'special' not in path:
        return
    print('  next_hop {:<16} -> {:<20}'.format(path['special'], path['ifname']))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    f = NxapiForwardingRouteUnicastIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    f.nxapi_init(cfg)
    f.prefix = cfg.prefix
    f.vrf = cfg.vrf
    try:
        f.module = int(cfg.module)
    except:
        log.error('worker: Early return from thread.  Expected integer for --module.  Got: {}'.format(cfg.module))
        return

    f.refresh()
    with lock:
        print('hostname {} prefix {} num_paths {}'.format(f.hostname, f.ip_prefix, f.num_paths))
        for path in f.path_info:
            if 'ip_nexthop' in path:
                print_path_ip_nexthop(path)
            if 'special' in path:
                print_path_special(path)

def verify_args():
    try:
        _ = int(cfg.module)
    except:
        log.error('exiting. Expected integer for --module.  Got: {}'.format(cfg.module))
        exit(1)
    v = VerifyTypes(log)
    if not v.is_ipv4_address_with_prefix(cfg.prefix):
        log.error('exiting. Expected ipv4 prefix of the form A.B.C.D/M. Got {}'.format(cfg.prefix))
        exit(1)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
verify_args()
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()
