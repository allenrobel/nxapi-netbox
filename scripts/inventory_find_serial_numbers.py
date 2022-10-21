#!/usr/bin/env python3
'''
Name: inventory_find_serial_numbers.py
Description: NXAPI: find one or more serial numbers across a set of NXOS switches

Example output:

% ./inventory_find_serial_numbers.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_l2_fanout,cvd_bgw_1 --serials FOC21055QF1,SAL1230Q3F5
ip              hostname             serial       name            product_id       description                   
192.168.11.116  cvd_l2_911           SAL1230Q3F5  Chassis         N3K-C3232C       Nexus3000 C3232C Chassis      
192.168.11.116  cvd_l2_911           SAL1230Q3F5  Slot 1          N3K-C3232C       32x40/100G QSFP28 2x10G SFP+ Ethernet Module

192.168.11.110  cvd-1111-bgw         FOC21055QF1  Slot 24         N9K-C9504-FM-E   4-slot Fabric Module          

% 

'''
our_version = 111
script_name = 'inventory_find_serial_numbers'

#standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_inventory import NxapiInventory

def get_parser():
    help_serials = 'a comma-separated list (no spaces) of Nexus serial numbers'
    ex_prefix = 'Example:'
    ex_serials = '{} --serials SAL2222U92Z,FOC321017XA,FOC543217XA'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: find one or more serial numbers across a set of NXOS switches.',
        parents=[ArgsCookie, ArgsNxapiTools])

    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    mandatory.add_argument('--serials',
                        dest='serials',
                        required=True,
                        help='(default: %(default)s) ' + help_serials + ex_serials,
                        )

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
def get_serial_number_list():
    try:
        return cfg.serials.split(',')
    except:
        log.error('exiting. Cannot parse --serials {}.  Example usage: --serials SAL2232U92Z,FOC321617XA,FOC631317XA'.format(cfg.serials))
        exit(1)

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)
        if len(output) > 0:
            print()

def print_header():
    print(fmt.format(
        'ip',
        'hostname',
        'serial',
        'name',
        'product_id',
        'description'))

def collect_output(ip, nx):
    lines = list()
    for item in nx.info:
        nx.item = item
        if nx.serialnum not in serial_numbers:
            continue
        lines.append(fmt.format(
            ip,
            nx.hostname,
            nx.serialnum,
            nx.name,
            nx.productid,
            nx.desc))
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInventory(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    return collect_output(ip, nx)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
serial_numbers = get_serial_number_list()

fmt = '{:<15} {:<20} {:<12} {:<15} {:<16} {:<30}'
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
