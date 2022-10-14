#!/usr/bin/env python3
'''
Name: interface_info.py
Description: NXAPI: display info from "show interface" cli

Synopsis:

./interface_info.py --vault hashicorp --device leaf_1,leaf_2
'''
our_version = 104
script_name = 'interface_info'

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

def get_parser():
    help_interface = 'interface to monitor'
    ex_interface = 'Example: --interface Eth1/1'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display info from "show interface" cli.',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    mandatory.add_argument('--interface',
                        dest='interface',
                        required=True,
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
    #log.info('d {}'.format(d))
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width

def print_header(d, width):
    print('{:<15} {:<15} {:<{width}} {}'.format('dut', 'interface', 'key', 'value', width=width))

def print_dict(d, hostname):
    width = get_max_width(d)
    if 'interface' not in d:
        log.error('skipping. [interface] key not found in dictionary {}'.format(d))
        return
    interface = d['interface']
    for key in sorted(d):
        value = d[key]
        print("{:<15} {:<15} {:<{width}} {}".format(hostname, interface, key, value, width=width))
    print()

def print_prop(hostname, interface, width, key, value):
    print("{:<15} {:<15} {:<{width}} {:<}".format(hostname, interface, key, value, width=width))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)
    i.interface = cfg.interface
    i.refresh()
    with lock:
        print()
        width = get_max_width(i.info)
        print_header(i.info, width)
        print_prop(i.hostname, i.interface, width, 'interface', i.interface)
        print_prop(i.hostname, i.interface, width, 'state', i.state)
        print_prop(i.hostname, i.interface, width, 'state_rsn_desc', i.state_rsn_desc)
        print_prop(i.hostname, i.interface, width, 'admin_state', i.admin_state)
        print_prop(i.hostname, i.interface, width, 'share_state', i.share_state)
        print_prop(i.hostname, i.interface, width, 'eth_hw_desc', i.eth_hw_desc)
        print_prop(i.hostname, i.interface, width, 'eth_hw_addr', i.eth_hw_addr)
        print_prop(i.hostname, i.interface, width, 'eth_bia_addr', i.eth_bia_addr)
        print_prop(i.hostname, i.interface, width, 'eth_mtu', i.eth_mtu)
        print_prop(i.hostname, i.interface, width, 'eth_bw', i.eth_bw)
        print_prop(i.hostname, i.interface, width, 'eth_dly', i.eth_dly)
        print_prop(i.hostname, i.interface, width, 'eth_reliability', i.eth_reliability)
        print_prop(i.hostname, i.interface, width, 'eth_txload', i.eth_txload)
        print_prop(i.hostname, i.interface, width, 'eth_rxload', i.eth_rxload)
        print_prop(i.hostname, i.interface, width, 'medium', i.medium)
        print_prop(i.hostname, i.interface, width, 'eth_duplex', i.eth_duplex)
        print_prop(i.hostname, i.interface, width, 'eth_speed', i.eth_speed)
        print_prop(i.hostname, i.interface, width, 'eth_beacon', i.eth_beacon)
        print_prop(i.hostname, i.interface, width, 'eth_autoneg', i.eth_autoneg)
        print_prop(i.hostname, i.interface, width, 'eth_in_flowctrl', i.eth_in_flowctrl)
        print_prop(i.hostname, i.interface, width, 'eth_out_flowctrl', i.eth_out_flowctrl)
        print_prop(i.hostname, i.interface, width, 'eth_mdix', i.eth_mdix)
        print_prop(i.hostname, i.interface, width, 'eth_swt_monitor', i.eth_swt_monitor)
        print_prop(i.hostname, i.interface, width, 'eth_ethertype', i.eth_ethertype)
        print_prop(i.hostname, i.interface, width, 'eth_eee_state', i.eth_eee_state)
        print_prop(i.hostname, i.interface, width, 'eth_link_flapped', i.eth_link_flapped)
        print_prop(i.hostname, i.interface, width, 'eth_clear_counters', i.eth_clear_counters)
        print_prop(i.hostname, i.interface, width, 'eth_reset_cntr', i.eth_reset_cntr)
        print_prop(i.hostname, i.interface, width, 'eth_load_interval1_rx', i.eth_load_interval1_rx)
        print_prop(i.hostname, i.interface, width, 'eth_inrate1_bits', i.eth_inrate1_bits)
        print_prop(i.hostname, i.interface, width, 'eth_inrate1_pkts', i.eth_inrate1_pkts)
        print_prop(i.hostname, i.interface, width, 'eth_load_interval1_tx', i.eth_load_interval1_tx)
        print_prop(i.hostname, i.interface, width, 'eth_outrate1_bits', i.eth_outrate1_bits)
        print_prop(i.hostname, i.interface, width, 'eth_outrate1_pkts', i.eth_outrate1_pkts)
        print_prop(i.hostname, i.interface, width, 'eth_inucast', i.eth_inucast)
        print_prop(i.hostname, i.interface, width, 'eth_inmcast', i.eth_inmcast)
        print_prop(i.hostname, i.interface, width, 'eth_inbcast', i.eth_inbcast)
        print_prop(i.hostname, i.interface, width, 'eth_inpkts', i.eth_inpkts)
        print_prop(i.hostname, i.interface, width, 'eth_inbytes', i.eth_inbytes)
        print_prop(i.hostname, i.interface, width, 'eth_jumbo_inpkts', i.eth_jumbo_inpkts)
        print_prop(i.hostname, i.interface, width, 'eth_storm_supp', i.eth_storm_supp)
        print_prop(i.hostname, i.interface, width, 'eth_runts', i.eth_runts)
        print_prop(i.hostname, i.interface, width, 'eth_giants', i.eth_giants)
        print_prop(i.hostname, i.interface, width, 'eth_crc', i.eth_crc)
        print_prop(i.hostname, i.interface, width, 'eth_nobuf', i.eth_nobuf)
        print_prop(i.hostname, i.interface, width, 'eth_inerr', i.eth_inerr)
        print_prop(i.hostname, i.interface, width, 'eth_frame', i.eth_frame)
        print_prop(i.hostname, i.interface, width, 'eth_overrun', i.eth_overrun)
        print_prop(i.hostname, i.interface, width, 'eth_underrun', i.eth_underrun)
        print_prop(i.hostname, i.interface, width, 'eth_ignored', i.eth_ignored)
        print_prop(i.hostname, i.interface, width, 'eth_watchdog', i.eth_watchdog)
        print_prop(i.hostname, i.interface, width, 'eth_bad_eth', i.eth_bad_eth)
        print_prop(i.hostname, i.interface, width, 'eth_bad_proto', i.eth_bad_proto)
        print_prop(i.hostname, i.interface, width, 'eth_in_ifdown_drops', i.eth_in_ifdown_drops)
        print_prop(i.hostname, i.interface, width, 'eth_dribble', i.eth_dribble)
        print_prop(i.hostname, i.interface, width, 'eth_indiscard', i.eth_indiscard)
        print_prop(i.hostname, i.interface, width, 'eth_inpause', i.eth_inpause)
        print_prop(i.hostname, i.interface, width, 'eth_outucast', i.eth_outucast)
        print_prop(i.hostname, i.interface, width, 'eth_outmcast', i.eth_outmcast)
        print_prop(i.hostname, i.interface, width, 'eth_outbcast', i.eth_outbcast)
        print_prop(i.hostname, i.interface, width, 'eth_outpkts', i.eth_outpkts)
        print_prop(i.hostname, i.interface, width, 'eth_outbytes', i.eth_outbytes)
        print_prop(i.hostname, i.interface, width, 'eth_jumbo_outpkts', i.eth_jumbo_outpkts)
        print_prop(i.hostname, i.interface, width, 'eth_outerr', i.eth_outerr)
        print_prop(i.hostname, i.interface, width, 'eth_coll', i.eth_coll)
        print_prop(i.hostname, i.interface, width, 'eth_deferred', i.eth_deferred)
        print_prop(i.hostname, i.interface, width, 'eth_latecoll', i.eth_latecoll)
        print_prop(i.hostname, i.interface, width, 'eth_lostcarrier', i.eth_lostcarrier)
        print_prop(i.hostname, i.interface, width, 'eth_nocarrier', i.eth_nocarrier)
        print_prop(i.hostname, i.interface, width, 'eth_babbles', i.eth_babbles)
        print_prop(i.hostname, i.interface, width, 'eth_outdiscard', i.eth_outdiscard)
        print_prop(i.hostname, i.interface, width, 'eth_outpause', i.eth_outpause)

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
