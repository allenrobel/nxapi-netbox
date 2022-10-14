#!/usr/bin/env python3
our_version = 104
'''
Name: forwarding_consistency.py
Description: NXAPI: start and display results for forwarding consistency checker
'''
script_name = 'forwarding_consistency'

# standard libraries
import argparse
from threading import Thread
from time import sleep
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_show import NxapiShow
from nxapi.nxapi_config import NxapiConfig


def get_parser():
    help_ipv6 = 'If present, test ipv6 forwarding consistency in addition to ipv4'
    help_time = 'Duration of inconsistency test, in seconds.  For larger prefix scales, you may need to increase this.'
    ex_prefix = 'Example: '
    ex_ipv6 = '{} --ipv6'.format(ex_prefix)
    ex_time = '{} --time 20'.format(ex_prefix)
    title = 'NXAPI: start and display results for forwarding consistency checker'
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: {}'.format(title),
        parents=[ArgsCookie,ArgsNxapiTools])
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    optional.add_argument('--time',
                        dest='time',
                        required=False,
                        default=10,
                        help='(default: %(default)s seconds) ' + help_time + ex_time)

    optional.add_argument('--ipv6',
                        dest='ipv6',
                        required=False,
                        default=False,
                        action='store_true',
                        help='(default: %(default)s) ' + help_ipv6 + ex_ipv6)

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + str(our_version))

    parser.set_defaults(ipv6=False)
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)

def run_config(ip, vault, cmd):
    nx = NxapiConfig(vault.nxos_username, vault.nxos_password, ip, log)
    cfg = list()
    cfg.append(cmd)
    nx.config_list = cfg
    nx.commit_list()

def run_command(ip, vault, cmd):
    nx = NxapiShow(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init()
    nx.cli = cmd
    nx.show()
    return nx.body[0]

def log_result_ipv4(device, ip, result):
    if 'run_status' not in result:
        log.error('{} ({}) IPV4 -> {}'.format(device, ip, result))
        return
    run_status = result['run_status'].strip()
    if 'PASS' not in run_status:
        log.warning('{} ({}) IPV4 -> {}'.format(device, ip, result))
        return
    log.info('{} ({}) IPV4 -> {}'.format(device, ip, run_status))

def log_result_ipv6(device, ip, result):
    if 'run_status' not in result:
        log.error('{} ({}) IPV6 -> {}'.format(device, ip, result))
        return
    run_status = result['run_status'].strip()
    if 'PASS' not in run_status:
        log.warning('{} ({}) IPV6 -> {}'.format(device, ip, result))
        return
    log.info('{} ({}) IPV6 -> {}'.format(device, ip, run_status))

def clear_consistency_results(ip, vault):
    '''
    this cli is a noop in NXOS as of irvine_934 build 17
    '''
    result = run_config(ip, vault, 'clear forwarding inconsistency')

def start_consistency_test_ipv4(ip, vault):
    result = run_config(ip, vault, 'test forwarding ipv4 unicast inconsistency')
def start_consistency_test_ipv6(ip, vault):
    result = run_config(ip, vault, 'test forwarding ipv6 unicast inconsistency')

def display_results_ipv4(device, ip, vault):
    result = run_command(ip, vault, 'show forwarding ipv4 unicast inconsistency')
    log_result_ipv4(device, ip, result)
def display_results_ipv6(device, ip, vault):
    result = run_command(ip, vault, 'show forwarding ipv6 unicast inconsistency')
    log_result_ipv6(device, ip, result)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    clear_consistency_results(ip, vault)
    start_consistency_test_ipv4(ip, vault)
    if cfg.ipv6 == True:
        start_consistency_test_ipv6(ip, vault)
    sleep(float(cfg.time))
    display_results_ipv4(device, ip, vault)
    if cfg.ipv6 == True:
        display_results_ipv6(device, ip, vault)
    print()

def verify_args():
    try:
        float(cfg.time)
    except:
        log.error('exiting.  Expected int() or float() for --time.  Got {}'.format(cfg.time))
        exit(1)

cfg = get_parser()
verify_args()

log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
log.info('Please wait...this could take a couple minutes.')
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()

