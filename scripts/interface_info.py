#!/usr/bin/env python3
'''
Name: interface_info.py
Description: NXAPI: display info from "show interface" cli

Synopsis:

./interface_info.py --vault hashicorp --device leaf_1,leaf_2
'''
our_version = 105
script_name = 'interface_info'

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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def get_max_width(d):
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width

def get_header(width):
    return fmt.format('ip', 'hostname', 'interface', 'key', 'value', width=width)

def collect_output_from_dict(ip, nx):
    lines = list()
    width = get_max_width(nx.info)
    if 'interface' not in nx.info:
        lines.append('{} {} skipping. [interface] key not found in dictionary {}'.format(ip, nx.hostname, nx.info))
        return lines
    lines.append(get_header(width))
    interface = nx.info['interface']
    for key in sorted(nx.info):
        value = nx.info[key]
        lines.append(fmt.format(ip, nx.hostname, interface, key, value, width=width))
    lines.append('')
    return lines

def get_item(ip, hostname, interface, width, key, value):
    return fmt.format(ip, hostname, interface, key, value, width=width)

def collect_output(ip, i):
    lines = list()
    lines.append('')
    width = get_max_width(i.info)
    lines.append(get_header(width))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'interface', i.interface))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'state', i.state))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'state_rsn_desc', i.state_rsn_desc))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'admin_state', i.admin_state))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'share_state', i.share_state))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_hw_desc', i.eth_hw_desc))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_hw_addr', i.eth_hw_addr))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_bia_addr', i.eth_bia_addr))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_mtu', i.eth_mtu))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_bw', i.eth_bw))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_dly', i.eth_dly))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_reliability', i.eth_reliability))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_txload', i.eth_txload))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_rxload', i.eth_rxload))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'medium', i.medium))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_duplex', i.eth_duplex))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_speed', i.eth_speed))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_beacon', i.eth_beacon))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_autoneg', i.eth_autoneg))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_in_flowctrl', i.eth_in_flowctrl))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_out_flowctrl', i.eth_out_flowctrl))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_mdix', i.eth_mdix))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_swt_monitor', i.eth_swt_monitor))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_ethertype', i.eth_ethertype))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_eee_state', i.eth_eee_state))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_link_flapped', i.eth_link_flapped))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_clear_counters', i.eth_clear_counters))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_reset_cntr', i.eth_reset_cntr))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_load_interval1_rx', i.eth_load_interval1_rx))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inrate1_bits', i.eth_inrate1_bits))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inrate1_pkts', i.eth_inrate1_pkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_load_interval1_tx', i.eth_load_interval1_tx))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outrate1_bits', i.eth_outrate1_bits))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outrate1_pkts', i.eth_outrate1_pkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inucast', i.eth_inucast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inmcast', i.eth_inmcast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inbcast', i.eth_inbcast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inpkts', i.eth_inpkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inbytes', i.eth_inbytes))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_jumbo_inpkts', i.eth_jumbo_inpkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_storm_supp', i.eth_storm_supp))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_runts', i.eth_runts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_giants', i.eth_giants))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_crc', i.eth_crc))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_nobuf', i.eth_nobuf))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inerr', i.eth_inerr))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_frame', i.eth_frame))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_overrun', i.eth_overrun))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_underrun', i.eth_underrun))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_ignored', i.eth_ignored))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_watchdog', i.eth_watchdog))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_bad_eth', i.eth_bad_eth))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_bad_proto', i.eth_bad_proto))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_in_ifdown_drops', i.eth_in_ifdown_drops))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_dribble', i.eth_dribble))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_indiscard', i.eth_indiscard))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_inpause', i.eth_inpause))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outucast', i.eth_outucast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outmcast', i.eth_outmcast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outbcast', i.eth_outbcast))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outpkts', i.eth_outpkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outbytes', i.eth_outbytes))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_jumbo_outpkts', i.eth_jumbo_outpkts))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outerr', i.eth_outerr))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_coll', i.eth_coll))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_deferred', i.eth_deferred))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_latecoll', i.eth_latecoll))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_lostcarrier', i.eth_lostcarrier))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_nocarrier', i.eth_nocarrier))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_babbles', i.eth_babbles))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outdiscard', i.eth_outdiscard))
    lines.append(get_item(ip, i.hostname, i.interface, width, 'eth_outpause', i.eth_outpause))
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.interface = cfg.interface
    nx.refresh()
    # display all items in nx.info
    return collect_output_from_dict(ip, nx)
    # selectively display items through property access
    # return collect_output(ip, nx)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:<15} {:<{width}} {:<10}'

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
