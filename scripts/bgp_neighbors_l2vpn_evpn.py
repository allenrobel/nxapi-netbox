#!/usr/bin/env python3
'''
Name: bgp_neighbors_l2vpn_evpn.py
Description: NXAPI: display bgp l2vpn evpn neighbor info
'''
our_version = 102
script_name = 'bgp_neighbors_l2vpn_evpn'
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
from nxapi.nxapi_bgp_l2vpn_evpn_summary import NxapiBgpL2vpnEvpnSummary

def get_parser():
    valid_bgp_state = ['Established', 'Idle']
    help_nonzero = 'if specified, only display neighbors with non-zero prefixes received'
    help_state = 'if specified, display neighbors with matching state.  Valid values: {}'.format(','.join(sorted(str(valid_bgp_state))))
    help_vrf = 'vrf in which to query bgp neighbors'
    ex_prefix = 'Example: '
    ex_nonzero = '{} --nonzero'.format(ex_prefix)
    ex_state = '{} --state Idle'.format(ex_prefix)
    ex_vrf = '{} --vrf myVrf'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display bgp l2vpn evpn neighbor info',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--nonzero',
                           dest='nonzero',
                           required=False,
                           default=False,
                           action='store_true',
                           help='{} {}'.format(help_nonzero, ex_nonzero))

    default.add_argument('--state',
                           dest='state',
                           required=False,
                           choices=valid_bgp_state,
                           default=None,
                           help='{} {}'.format(help_state, ex_state))

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

def collect_output(ip, nx, lines):
    lines.append(fmt.format(ip, nx.hostname, 'neighborid', nx.neighborid))
    lines.append(fmt.format(ip, nx.hostname, 'neighborversion', nx.neighborversion))
    lines.append(fmt.format(ip, nx.hostname, 'msgrecvd', nx.msgrecvd))
    lines.append(fmt.format(ip, nx.hostname, 'msgsent', nx.msgsent))
    lines.append(fmt.format(ip, nx.hostname, 'neighbortableversion', nx.neighbortableversion))
    lines.append(fmt.format(ip, nx.hostname, 'inq', nx.inq))
    lines.append(fmt.format(ip, nx.hostname, 'outq', nx.outq))
    lines.append(fmt.format(ip, nx.hostname, 'neighboras', nx.neighboras))
    lines.append(fmt.format(ip, nx.hostname, 'time', nx.time))
    lines.append(fmt.format(ip, nx.hostname, 'state', nx.state))
    lines.append(fmt.format(ip, nx.hostname, 'prefixreceived', nx.prefixreceived))
    lines.append('{}'.format(' '))

def show_bgp_neighbors_l2vpn_evpn(ip, nx, state=None):
    lines = list()
    for neighbor in nx.neighbor_info:
        nx.neighbor = neighbor
        if state != None:
            if state != nx.state:
                continue
        try:
            prefixreceived = int(nx.prefixreceived)
        except:
            log.error('exiting. cannot convert nx.prefixreceived {} to int()'.format(nx.prefixreceived))
            exit(1)
        if prefixreceived == 0 and cfg.nonzero == True:
            continue
        collect_output(ip, nx, lines)
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiBgpL2vpnEvpnSummary(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vrf = cfg.vrf
    nx.refresh()
    return show_bgp_neighbors_l2vpn_evpn(ip, nx, cfg.state)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<4} {:<14} {:<20} {:>14}'

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
