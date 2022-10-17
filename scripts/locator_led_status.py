#!/usr/bin/env python3
'''
Name: locator_led_status.py
Description: NXAPI: display locator-led status for chassis, modules, fans
'''
our_version = 104
script_name = 'locator_led_status'

#standard libraries
import argparse
import re
from threading import Thread, Lock
# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_locator_led import NxapiLocatorLedStatus

def get_parser():
    ex_prefix = 'Example:'
    help_module = 'Either a single module/linecard, or a comma-separate list of modules/linecards'
    help_fan = 'Either a single fan, or a comma-separate list of fans'
    help_on = 'If present, print only locator-leds whose status is ON. If not present, print status for all locator-leds'
    ex_module = '{} --module 2,3,6'.format(ex_prefix)
    ex_fan = '{} --fan 3'.format(ex_prefix)
    ex_on = '{} --on'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display locator-led status for chassis, modules, fans',
        parents=[ArgsCookie, ArgsNxapiTools])
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')

    optional.add_argument('--on',
                        dest='on',
                        required=False,
                        action='store_true',
                        default=False,
                        help='{} {}'.format(help_on, ex_on))
    optional.add_argument('--module',
                        dest='module',
                        required=False,
                        default=None,
                        help='(default: %(default)s) ' + help_module + ex_module,
                        )
    optional.add_argument('--fan',
                        dest='fan',
                        required=False,
                        default=None,
                        help='(default: %(default)s) ' + help_fan + ex_fan,
                        )

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
    print(fmt.format('status', 'locator-led', 'hostname'))

def print_items(led, modules, fans):
    if not cfg.on:
        print(fmt.format(led.chassis, 'chassis', led.hostname))
    elif cfg.on and led.chassis == 'ON':
        print(fmt.format(led.chassis, 'chassis', led.hostname))
    for module in modules:
        led.module = module
        if cfg.on and led.module_status != 'ON':
            continue
        print(fmt.format(led.module_status, 'module_{}'.format(module), led.hostname))
    for fan in fans:
        led.fan = fan
        if cfg.on and led.fan_status != 'ON':
            continue
        print(fmt.format(led.fan_status, 'fan_{}'.format(fan), led.hostname))

def worker(device, vault, modules, fans):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiLocatorLedStatus(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    with lock:
        print_items(nx, modules, fans)

def cfg_to_list(cfg_list, desc):
    _list = list()
    if cfg_list == None:
        return _list
    for item in re.split(',', str(cfg_list)):
        if item == None:
            continue
        try:
            _list.append(int(item))
        except:
            log.error('Exiting. Expected int() for {}. Got {}'.format(desc, cfg_list))
            log.error('Usage examples:')
            log.error('    --{} 3'.format(desc))
            log.error('    --{} 1,2,4'.format(desc))
            exit(1)
    return _list


cfg = get_parser()
modules = cfg_to_list(cfg.module, 'module')
fans = cfg_to_list(cfg.fan, 'fan')
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '{:<6} {:<12} {:<16}'
print_header()
lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault, modules, fans))
    t.start()
