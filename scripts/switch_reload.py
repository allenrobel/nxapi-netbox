#!/usr/bin/env python3
'''
Name: switch_reload.py
Description: NXAPI: reload (or install reset) one or more NX-OS devices
Synopsis:

./switch_reload.py --vault hashicorp --device leaf_1,leaf_2
'''
our_version = 105
script_name = 'switch_reload.py'

# standard libraries
import argparse
from threading import Thread

# local libraries
from args.args_cookie import ArgsCookie
from args.args_nxapi_tools import ArgsNxapiTools
from general.log import get_logger
from netbox.netbox_session import netbox, get_device_mgmt_ip
from netbox.device import Device
from vault.vault import get_vault
from nxapi.nxapi_config import NxapiConfig

def get_parser():
    help_install_reset = 'If present, use install reset, instead of reload.  If not present, the default is to use reload'
    ex_install_reset = 'Example: --install_reset'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: reload (or install reset) one or more NX-OS devices',
                                    parents=[ArgsCookie, ArgsNxapiTools])
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    optional.add_argument('--install_reset',
                        dest='install_reset',
                        required=False,
                        default=False,
                        action='store_true',
                        help='{} {}'.format(help_install_reset, ex_install_reset))

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

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    c = NxapiConfig(vault.nxos_username, vault.nxos_password, ip, log)
    c.nxapi_init(cfg)
    c.timeout = 5
    if cfg.install_reset == True:
        errmsg = 'worker. exiting. Unable to install reset hostname {} ip {}'.format(c.hostname, ip)
        c.config_list = ['install reset']
    else:
        errmsg = 'worker. exiting. Unable to reload hostname {} ip {}'.format(c.hostname, ip)
        c.config_list = ['reload in 5']
    try:
        c.commit_list()
    except:
        log.error(errmsg)
        exit(1)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
