#!/usr/bin/env python3
our_version = 108
'''
Name: interface_beacon_status.py
Description: NXAPI: display interface beacon status

Example usage:

./interface_beacon_status.py --vault hashicorp --devices leaf_1,leaf_2 [--interface Eth1/1] [--on]

NOTES:

   1. mgmt0 is non-virtual, and currently does not support beacon.  We process it anyway in case it ever 
      does support beacon
'''
script_name = 'interface_beacon_status'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_interface import NxapiInterface
from nxapi.nxapi_interface import NxapiInterfaceStatus

help_interface = 'If present, interface to monitor.  If not present, all interfaces will be monitored.'
help_on = 'If present, print only interfaces whose beacon status is on. If not present, print all interface beacon status.'

ex_interface = 'Example: --interface Eth1/1'
ex_on = 'Example: --on'

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display interface beacon status.',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--interface',
                        dest='interface',
                        required=False,
                        default=None,
                        help='{} {}'.format(help_interface, ex_interface))

    default.add_argument('--on',
                        dest='on',
                        required=False,
                        action='store_true',
                        default=False,
                        help='{} {}'.format(help_on, ex_on))

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

def print_header():
    print(fmt.format('ip', 'hostname', 'interface', 'state', 'admin', 'beacon', 'dut'))

def get_values(ip, hostname, interface, state, admin, beacon):
    if cfg.on == True and (beacon == 'off' or beacon == 'na'):
        return None
    return fmt.format(ip, hostname, interface, state, admin, beacon)

def collect_output(ip, interface_status, interface_detail):
    lines = list()
    for interface in interface_status.info:
        if interface_detail.is_virtual_interface(interface):
            continue
        interface_detail.interface = interface
        interface_detail.refresh()
        x = get_values(ip,
            interface_detail.hostname,
            interface_detail.interface,
            interface_detail.state,
            interface_detail.admin_state,
            interface_detail.eth_beacon)
        if x != None:
            lines.append(x)
    if len(lines) != 0:
        lines.append('')
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)

    s = NxapiInterfaceStatus(vault.nxos_username, vault.nxos_password, ip, log)
    s.nxapi_init(cfg)
    s.interface = cfg.interface
    s.refresh()

    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    return collect_output(ip, s, i)


fmt = '{:<15} {:<18} {:<15} {:<7} {:<7} {:<6}'
cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
