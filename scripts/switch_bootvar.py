#!/usr/bin/env python3
our_version = 105
script_name = 'switch_bootvar'
'''
Name: switch_bootvar.py
Description: NXAPI: display current bootvar info

If not specified, --sup_instance defaults to 1:

./switch_bootvar.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2

Explictly specifying sup_instance:

./switch_bootvar.py --vault hashicorp --devices cvd_bgw_1,cvd_bgw_2 --sup_instance 2

Example output:

% ./switch_bootvar.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_bgw_1
ip              hostname             sup poap_status current_image                            startup_image                           
192.168.11.102  cvd-1311-leaf        1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
192.168.11.103  cvd-1312-leaf        1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
192.168.11.110  cvd-1111-bgw         1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
%
'''
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_boot import NxapiBoot

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display current bootvar info.',
            parents=[ArgsCookie, ArgsNxapiTools])
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    help_sup_instance = 'If present, the supervisor module instance to query'
    ex_sup_instance = '--sup_instance 2'

    default.add_argument('--sup_instance',
                        dest='sup_instance',
                        required=False,
                        default=1,
                        help='default {} {} {}'.format('%(default)s', help_sup_instance, ex_sup_instance))

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
    print(fmt.format('ip', 'hostname', 'sup', 'poap_status', 'current_image', 'startup_image'))

def get_info(ip, nx):
    return fmt.format(
        ip,
        nx.hostname,
        nx.sup_instance,
        nx.current_poap_status,
        nx.current_image,
        nx.startup_image)

def worker(device, vault):
    lines = list()
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiBoot(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    nx.sup_instance = sup_instance
    lines.append(get_info(ip, nx))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

try:
    sup_instance = int(cfg.sup_instance)
except:
    log.error('Exiting. Expected integer for --sup_instance. Got {}'.format(cfg.sup_instance))
    exit(1)

fmt = '{:<15} {:<20} {:<3} {:<11} {:<40} {:<40}'
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
