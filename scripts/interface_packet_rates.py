#!/usr/bin/env python3
'''
Name: interface_packet_rates.py
Description: NXAPI: display interface input/output packet rates for a set of interfaces

Example usage:

./nxapi_interface_packet_rates.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2 --interfaces Eth1/1,Eth1/2

'''
our_version = 106
script_name = 'nxapi_interface_packet_rates'

# standard libraries
import argparse
from threading import Thread, Lock
from os import path
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_interface import NxapiInterface

help_interfaces = 'Comma-separated list (no spaces) of interfaces to monitor'
ex_interfaces = 'Example --interfaces Eth1/1,Eth1/2'

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: monitor interface input/output packet rates for a set of interfaces',
        parents=[ArgsCookie, ArgsNxapiTools])
    optional = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    mandatory.add_argument('--interfaces',
                        dest='interfaces',
                        required=True,
                        help='{} {}'.format(help_interfaces, ex_interfaces))

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + str(our_version))
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)

def get_interface_list():
    try:
        return cfg.interfaces.split(',')
    except:
        log.error('exiting. Cannot parse --interfaces {}.  Example usage: --interfaces Eth1/1,Eth1/2'.format(cfg.interfaces))
        exit(1)

def worker(device, vault, interfaces):
    ip = get_device_mgmt_ip(nb, device)

    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    with lock:
        for interface in interfaces:
            i.interface = interface
            result = i.refresh()
            if not result:
                return
            eth_outrate1_pkts = i.info['eth_outrate1_pkts']
            eth_inrate1_pkts = i.info['eth_inrate1_pkts']
            print(fmt.format(i.hostname, interface, eth_outrate1_pkts, 'output packet rate'))
            print(fmt.format(i.hostname, interface, eth_inrate1_pkts, 'input packet rate'))
        print()


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
interfaces = get_interface_list()

fmt = '{:<6} {:<7} {:>10}  {:<18}'
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault, interfaces))
    t.start()
