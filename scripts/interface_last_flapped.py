#!/usr/bin/env python3
'''
Name: interface_last_flapped.py
Description: NXAPI: display interface last flapped/cleared timers, and reset info

Timers are converted to seconds.

Synopsis:

./nxapi_interface_last_flapped.py --vault hashicorp --device leaf_1,leaf_2 [--interface Eth1/1]
'''
our_version = 104
script_name = 'interface_last_flapped'

# standard libraries
import argparse
from threading import Thread, Lock

# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_interface import NxapiInterface
from nxapi.nxapi_interface import NxapiInterfaceStatus

def get_parser():
    help_interface = 'If present, interface to monitor.  If not present, all interfaces will be monitored.'
    ex_interface = 'Example: --interface Eth1/1'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display interface last flapped/cleared timers, and reset info',
        parents=[ArgsCookie, ArgsNxapiTools])
    optional = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    optional.add_argument('--interface',
                        dest='interface',
                        required=False,
                        default=None,
                        help='{} {}'.format(help_interface, ex_interface))

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

def get_max_width(d):
    '''
    not used
    '''
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width

def print_header():
    print(fmt.format('dut', 'interface', 'state', 'admin', 'flapped', 'cleared', 'resets'))

def print_values(hostname, interface, state, admin, flapped, cleared, resets):
    print(fmt.format(hostname, interface, state, admin, flapped, cleared, resets))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)

    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)

    # used to get the list of interfaces from s.info
    s = NxapiInterfaceStatus(vault.nxos_username, vault.nxos_password, ip, log)
    s.nxapi_init(cfg)
    s.interface = cfg.interface
    s.refresh()
    with lock:
        for interface in s.info:
            i.interface = interface
            i.refresh()
            print_values(i.hostname, i.interface, i.state, i.admin_state, i.eth_link_flapped, i.eth_clear_counters, i.eth_reset_cntr)
        print()
cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<15} {:<7} {:<7} {:<9} {:<9} {:<6}'
print_header()

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
