#!/usr/bin/env python3
'''
Name: bgp_neighbor_state.py
Description: NXAPI: display bgp neighbor state for all neighbors

Synopsis:

ipv4 neighbor state:

./bgp_neighbor_state.py --vault hashicorp --devices cvd_leaf_1

ipv6 neighbor state:

./nxapi_bgp_neighbor_state_sid.py --vault hashicorp --devices cvd_leaf_1 --ipv6
'''
our_version = 105
script_name = 'bgp_neighbor_state'

# standard libraries
import argparse
from threading import Thread, Lock

# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from scripts.arp_summary import get_device_list
from vault.vault import get_vault
from nxapi.nxapi_bgp_neighbors import NxapiBgpNeighborsIpv4, NxapiBgpNeighborsIpv6

def get_parser():
    ex_ipv6 = ' Example: --ipv6'
    help_ipv6 = 'If present, show ipv6 bgp neighbor state, else show ipv4 bgp neighbor state.'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display bgp neighbor state for all neighbors.',
        parents=[ArgsCookie,ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    mandatory.add_argument('--ipv6',
                        dest='ipv6',
                        required=False,
                        action='store_true',
                        default=False,
                        help='{} {} {}'.format('DEFAULT: %(default)s.', help_ipv6, ex_ipv6))

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
    print(fmt.format('hostname', 'peer', 'state', 'remote_as', 'sourceif', 'up', 'resettime'))

def worker(ip, vault):
    if cfg.ipv6 == True:
        bgp = NxapiBgpNeighborsIpv6(vault.nxos_username, vault.nxos_password, ip, log)
    elif cfg.ipv6 == False:
        bgp = NxapiBgpNeighborsIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    else:
        log.error('Exiting. unknown value for --ipv6')
        exit(1)
    bgp.nxapi_init(cfg)
    bgp.refresh()
    with lock:
        for peer in bgp.peers:
            bgp.peer = peer
            print(fmt.format(
                bgp.hostname,
                peer,
                bgp.state,
                bgp.remoteas,
                bgp.sourceif,
                bgp.up,
                bgp.resettime))

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<18} {:<20} {:<11} {:<11} {:<15} {:<5} {:<10}'
print_header()

lock = Lock()
for device in devices:
    ip = get_device_mgmt_ip(nb, device)
    t = Thread(target=worker, args=(ip, vault))
    t.start()
