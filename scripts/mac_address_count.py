#!/usr/bin/env python3
'''
Name: mac_address_count.py
Description: NXAPI: display mac address-table count
'''
our_version = 105
script_name = 'mac_address_count'

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
from nxapi.nxapi_mac_address_table import NxapiMacCount
from nxapi.nxapi_vlan import NxapiVlanId

def get_parser():
    help_vlan = 'the vlan in which to query mac address-table count. If not specified, printed values represent totals for all vlans'
    ex_vlan = '--vlan 42'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display mac address-table count',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--vlan',
                        dest='vlan',
                        required=False,
                        default=0,
                        help='default {} {} {}'.format('%(default)s', help_vlan, ex_vlan))

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

def verify_vlan(ip, vault):
    if cfg.vlan == 0:
        return True
    nx = NxapiVlanId(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vlan = cfg.vlan
    nx.refresh()
    if not nx.vlan_id:
        log.error('Exiting. vlan {} does not exist on {}.'.format(cfg.vlan, nx.hostname))
        return False
    return True

def print_header():
    print(fmt.format('ip', 'device', 'vlan', 'total', 'dyn', 'otv', 'rvtep', 'static', 'secure'))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    if not verify_vlan(ip, vault):
        return
    nx = NxapiMacCount(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vlan = cfg.vlan
    nx.refresh()
    if nx.vlan == 0:
        vlan = 'all'
    else:
        vlan = nx.vlan
    with lock:
        print(fmt.format(
            ip,
            nx.hostname,
            vlan,
            nx.total_cnt,
            nx.dyn_cnt,
            nx.otv_cnt,
            nx.rvtep_static_cnt,
            nx.static_cnt,
            nx.secure_cnt))

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<15} {:<18} {:>4} {:>7} {:>7} {:>7} {:>5} {:>7} {:>7}'
print_header()
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
