#!/usr/bin/env python3
'''
Name: interface_egress_queuing.py
Description: NXAPI: display interface egress queing information

Synopsis:

./interface_egress_queuing.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2  --interface Ethernet1/1 --qos 1,3,span,cpu
'''
our_version = 105
script_name = 'interface_egress_queuing'

# standard libraries
import argparse
from threading import Thread, Lock
from re import split
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_interface_egress_queuing import NxapiInterfaceEgressQueuing

def get_parser():
    help_interface = 'Interface(s) to monitor.'
    help_qos = 'QOS group(s) to monitor. Default: QOS group 0 will be monitored.'
    help_non_zero = 'If present, display only non-zero counters.'
    ex_interface = 'Example: --interface Eth1/1'
    ex_qos = 'Example: --qos 0,1,cpu,span'
    ex_non_zero = 'Example: --non_zero'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: display interface queuing information using NXAPI.',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--non_zero',
                        dest='non_zero',
                        required=False,
                        action='store_true',
                        help='{} {}'.format(help_non_zero, ex_non_zero))

    mandatory.add_argument('--interface',
                        dest='interface',
                        required=False,
                        default=None,
                        help='{} {}'.format(help_interface, ex_interface))

    default.add_argument('--qos',
                        dest='qos',
                        required=False,
                        default=0,
                        help='{} {}'.format(help_qos, ex_qos))

    parser.add_argument('--version',
                        action='version',
                        version='{} v{}'.format('%(prog)s', our_version))
    default.set_defaults(non_zero=False)
    default.set_defaults(qos=0)
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)

def get_interface_list():
    try:
        return cfg.interface.split(',')
    except:
        log.error('exiting. Cannot parse --interface {}.  Example usage: --interface Ethernet1/1'.format(cfg.interface))
        exit(1)

def print_head():
    print(fmt.format(
        'ip',
        'hostname',
        'interface',
        'qos_group',
        'type',
        'units',
        'protocol',
        'value'))

def print_values(ip, hostname, interface, qos_group, units, protocol, value, stat_type):
    if cfg.non_zero == True and value == 0:
        return
    if cfg.non_zero == True and value == 'na':
        return
    line = fmt.format(
        ip,
        hostname,
        interface,
        'qos_{}'.format(qos_group),
        stat_type,
        units,
        protocol,
        value)
    lines.append(line)

def get_list_from_comma_separated_string(x):
    if ',' in str(x):
        return split(',', str(x))
    else:
        return [x]

def worker(device, interface, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInterfaceEgressQueuing(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.interface = interface
    nx.refresh()
    with lock:
        nx.unit = 'packets'
        nx.protocol = 'uc'
        for qos_group in get_list_from_comma_separated_string(cfg.qos):
            nx.qos_group = qos_group
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.ecn, 'ecn')
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.tx, 'tx')
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.tail_drop, 'tail_drop')
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.wd_tail_drop, 'wd_tail_drop')
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.wred_afd_tail_drop, 'wred_afd_tail_drop')
        nx.unit = 'bytes'
        for qos_group in get_list_from_comma_separated_string(cfg.qos):
            nx.qos_group = qos_group
            print_values(ip, nx.hostname, nx.interface, nx.qos_group, nx.unit, nx.protocol, nx.q_depth, 'q_depth')


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
if len(devices) > 1:
    log.error('exiting. This script supports only one target device. Got --devicess {}'.format(devices))
    exit(1)

fmt = '{:<15} {:<18} {:<15} {:<9} {:<18} {:<8} {:>15} {:>15}'
print_head()
lock = Lock()

lines = list()
for interface in get_list_from_comma_separated_string(cfg.interface):
    t = Thread(target=worker, args=(devices[0], interface, vault))
    t.start()
    t.join(timeout=30.0)
for line in sorted(lines):
    print(line)
