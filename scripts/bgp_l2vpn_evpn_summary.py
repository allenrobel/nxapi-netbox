#!/usr/bin/env python3
'''
Name: bgp_l2vpn_evpn_summary.py
Description: NXAPI: display bgp l2vpn evpn summary

Sample output

% ./bgp_l2vpn_evpn_summary.py --vault hashicorp --devices cvd_leaf_1
192.168.20.101 cvd-1311-leaf  afi                      25
192.168.20.101 cvd-1311-leaf  safi                     70
192.168.20.101 cvd-1311-leaf  af_name          L2VPN EVPN
192.168.20.101 cvd-1311-leaf  table_version             4
192.168.20.101 cvd-1311-leaf  configured_peers          2
192.168.20.101 cvd-1311-leaf  capable_peers             2
192.168.20.101 cvd-1311-leaf  total_networks            0
192.168.20.101 cvd-1311-leaf  total_paths               0

%
'''
our_version = 104
script_name = 'bgp_l2vpn_evpn_summary'
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_bgp_l2vpn_evpn_summary import NxapiBgpL2vpnEvpnSummary

def get_parser():
    help_nonzero = 'if specified, only display neighbors with non-zero prefixes received'
    ex_prefix = 'Example: '
    ex_nonzero = '{} --nonzero'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display bgp l2vpn evpn summary',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--nonzero',
                           dest='nonzero',
                           required=False,
                           default=False,
                           action='store_true',
                           help='{} {}'.format(help_nonzero, ex_nonzero))

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

def collect_bgp_l2vpn_evpn_summary(ip, nx):
    lines = list()
    lines.append(fmt.format(ip, nx.hostname, 'afi', nx.af_id))
    lines.append(fmt.format(ip, nx.hostname, 'safi', nx.safi))
    lines.append(fmt.format(ip, nx.hostname, 'af_name', nx.af_name))
    lines.append(fmt.format(ip, nx.hostname, 'table_version', nx.tableversion))
    lines.append(fmt.format(ip, nx.hostname, 'configured_peers', nx.configuredpeers))
    lines.append(fmt.format(ip, nx.hostname, 'capable_peers', nx.capablepeers))
    lines.append(fmt.format(ip, nx.hostname, 'total_networks', nx.totalnetworks))
    lines.append(fmt.format(ip, nx.hostname, 'total_paths', nx.totalpaths))
    lines.append('{}'.format(' '))
    return lines

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiBgpL2vpnEvpnSummary(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vrf = cfg.vrf
    nx.refresh()
    return collect_bgp_l2vpn_evpn_summary(ip, nx)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

fmt = '{:<4} {:<14} {:<16} {:>10}'
devices = get_device_list()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
