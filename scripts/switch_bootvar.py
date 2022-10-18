#!/usr/bin/env python3
our_version = 103
script_name = 'switch_bootvar'
'''
Name: switch_bootvar.py
Description: NXAPI: show the current bootvar strings

If not specified, --sup_instance defaults to 1

./switch_bootvar.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2

Explictly specifying sup_instance

./switch_bootvar.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2 --sup_instance 2

Example output

% ./switch_bootvar.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_bgw_1
ip              hostname             sup poap_status current_image                            startup_image                           
192.168.11.102  cvd-1311-leaf        1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
192.168.11.103  cvd-1312-leaf        1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
192.168.11.110  cvd-1111-bgw         1   Disabled    bootflash:/nxos64-cs.10.2.3.F.bin        bootflash:/nxos64-cs.10.2.3.F.bin       
%
'''
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
from nxapi.nxapi_boot import NxapiBoot

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: show the current bootvar strings.',
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

def print_header():
    print(fmt.format('ip', 'hostname', 'sup', 'poap_status', 'current_image', 'startup_image'))

def print_info(ip, output):
    print(fmt.format(
        ip,
        output[ip].hostname,
        output[ip].sup_instance,
        output[ip].current_poap_status,
        output[ip].current_image,
        output[ip].startup_image))

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiBoot(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    nx.sup_instance = sup_instance
    output[ip] = nx

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
output = dict()
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()

for ip in sorted(output):
    print_info(ip, output)
