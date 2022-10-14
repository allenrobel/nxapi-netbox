#!/usr/bin/env python3
'''
Name: nxapi_bfd_neighbor_info_sid.py
Author: Allen Robel 
Email: arobel@cisco.com
Description: print show bfd neighbors detail information using NXAPI

'''
our_version = 106
script_name = 'nxapi_bfd_neighbor_info_sid'

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
from nxapi.nxapi_bfd import NxapiBfdNeighbors

ex_ipv6 = ' Example: --ipv6'
help_ipv6 = 'If present, show ipv6 bgp neighbor state, else show ipv4 bgp neighbor state.'

def get_parser():
    parser = argparse.ArgumentParser(description='DESCRIPTION: print bfd neighbors detail information using NXAPI.', parents=[ArgsCookie, ArgsNxapiTools])
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

def get_max_width(d):
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width

def print_head(width):
    print('{:<15} {:<15} {:<{width}} {:<}'.format('dut', 'interface', 'key', 'value', width=width))

def print_prop(hostname, interface, width, key, value):
    print("{:<15} {:<15} {:<{width}} {:<}".format(hostname, interface, key, value, width=width))

def print_info(d, hostname):
    width = get_max_width(d)
    if 'local_disc' not in d:
        log.error('skipping. [local_disc] key not found in dictionary {}'.format(d))
        return
    local_disc = d['local_disc']
    for key in sorted(d):
        value = d[key]
        print("{:<15} {:<15} {:<{width}} {:<}".format(hostname, local_disc, key, value, width=width))
    print()

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bfd = NxapiBfdNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    if cfg.ipv6 == True:
        bfd.ipv6 = True
    bfd.nxapi_init(cfg)
    bfd.refresh()

    if len(bfd.info) == 0:
        print("{} no bfd neighbors found".format(bfd.hostname))
        exit(0)
    else:
        print('{} {} bfd neighbors'.format(bfd.hostname, len(bfd.info)))
    key = list(bfd.info.keys())[0]
    width = get_max_width(bfd.info[key])
    with lock:
        # We could use a for loop to cycle through all keys in bfd_info.
        # Below is just to demonstrate explicit @property access
        print_head(width)
        for local_disc in bfd.info:
            bfd.local_disc = local_disc
            print_prop(bfd.hostname, bfd.intf, width, 'local_disc', bfd.local_disc)
            print_prop(bfd.hostname, bfd.intf, width, 'header', bfd.header)
            print_prop(bfd.hostname, bfd.intf, width, 'vrf_name', bfd.vrf_name)
            print_prop(bfd.hostname, bfd.intf, width, 'src_ip_addr', bfd.src_ip_addr)
            print_prop(bfd.hostname, bfd.intf, width, 'src_ipv6_addr', bfd.src_ipv6_addr)
            print_prop(bfd.hostname, bfd.intf, width, 'dest_ip_addr', bfd.dest_ip_addr)
            print_prop(bfd.hostname, bfd.intf, width, 'dest_ipv6_addr', bfd.dest_ipv6_addr)
            print_prop(bfd.hostname, bfd.intf, width, 'remote_disc', bfd.remote_disc)
            print_prop(bfd.hostname, bfd.intf, width, 'local_state', bfd.local_state)
            print_prop(bfd.hostname, bfd.intf, width, 'remote_state', bfd.remote_state)
            print_prop(bfd.hostname, bfd.intf, width, 'holddown', bfd.holddown)
            print_prop(bfd.hostname, bfd.intf, width, 'cur_detect_mult', bfd.cur_detect_mult)
            print_prop(bfd.hostname, bfd.intf, width, 'intf', bfd.intf)
            print_prop(bfd.hostname, bfd.intf, width, 'out_str', bfd.out_str)
            print_prop(bfd.hostname, bfd.intf, width, 'echo', bfd.echo)
            print_prop(bfd.hostname, bfd.intf, width, 'echo_tx', bfd.echo_tx)
            print_prop(bfd.hostname, bfd.intf, width, 'local_diag', bfd.local_diag)
            print_prop(bfd.hostname, bfd.intf, width, 'demand', bfd.demand)
            print_prop(bfd.hostname, bfd.intf, width, 'poll', bfd.poll)
            print_prop(bfd.hostname, bfd.intf, width, 'min_tx', bfd.min_tx)
            print_prop(bfd.hostname, bfd.intf, width, 'min_rx', bfd.min_rx)
            print_prop(bfd.hostname, bfd.intf, width, 'local_multi', bfd.local_multi)
            print_prop(bfd.hostname, bfd.intf, width, 'detect_timer', bfd.detect_timer)
            print_prop(bfd.hostname, bfd.intf, width, 'down_count', bfd.down_count)
            print_prop(bfd.hostname, bfd.intf, width, 'tx_interval', bfd.tx_interval)
            print_prop(bfd.hostname, bfd.intf, width, 'rx_count', bfd.rx_count)
            print_prop(bfd.hostname, bfd.intf, width, 'rx_avg', bfd.rx_avg)
            print_prop(bfd.hostname, bfd.intf, width, 'rx_min', bfd.rx_min)
            print_prop(bfd.hostname, bfd.intf, width, 'rx_max', bfd.rx_max)
            print_prop(bfd.hostname, bfd.intf, width, 'last_rx', bfd.last_rx)
            print_prop(bfd.hostname, bfd.intf, width, 'tx_count', bfd.tx_count)
            print_prop(bfd.hostname, bfd.intf, width, 'tx_avg', bfd.tx_avg)
            print_prop(bfd.hostname, bfd.intf, width, 'tx_min', bfd.tx_min)
            print_prop(bfd.hostname, bfd.intf, width, 'tx_max', bfd.tx_max)
            print_prop(bfd.hostname, bfd.intf, width, 'last_tx', bfd.last_tx)
            print_prop(bfd.hostname, bfd.intf, width, 'app', bfd.app)
            print_prop(bfd.hostname, bfd.intf, width, 'up_time', bfd.up_time)
            print_prop(bfd.hostname, bfd.intf, width, 'version', bfd.version)
            print_prop(bfd.hostname, bfd.intf, width, 'diag', bfd.diag)
            print_prop(bfd.hostname, bfd.intf, width, 'state_bit', bfd.state_bit)
            print_prop(bfd.hostname, bfd.intf, width, 'demand_bit', bfd.demand_bit)
            print_prop(bfd.hostname, bfd.intf, width, 'poll_bit', bfd.poll_bit)
            print_prop(bfd.hostname, bfd.intf, width, 'final_bit', bfd.final_bit)
            print_prop(bfd.hostname, bfd.intf, width, 'multiplier', bfd.multiplier)
            print_prop(bfd.hostname, bfd.intf, width, 'length', bfd.length)
            print_prop(bfd.hostname, bfd.intf, width, 'my_disc', bfd.my_disc)
            print_prop(bfd.hostname, bfd.intf, width, 'your_disc', bfd.your_disc)
            print_prop(bfd.hostname, bfd.intf, width, 'min_tx_interval', bfd.min_tx_interval)
            print_prop(bfd.hostname, bfd.intf, width, 'req_min_rx', bfd.req_min_rx)
            print_prop(bfd.hostname, bfd.intf, width, 'min_echo_interval', bfd.min_echo_interval)
            print_prop(bfd.hostname, bfd.intf, width, 'host_lc', bfd.host_lc)
            print_prop(bfd.hostname, bfd.intf, width, 'down_reason', bfd.down_reason)
            print_prop(bfd.hostname, bfd.intf, width, 'no_host_reason', bfd.no_host_reason)
            print_prop(bfd.hostname, bfd.intf, width, 'parent', bfd.parent)
            print_prop(bfd.hostname, bfd.intf, width, 'per_link_str', bfd.per_link_str)
            print_prop(bfd.hostname, bfd.intf, width, 'auth', bfd.auth)
            print_prop(bfd.hostname, bfd.intf, width, 'auth_bit', bfd.auth_bit)
            print_prop(bfd.hostname, bfd.intf, width, 'print_details', bfd.print_details)
            print('')

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

lock = Lock()
devices = get_device_list()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
