#!/usr/bin/env python3
'''
Name: switch_find_files.py
Description: NXAPI: find files whose name contains --find <string> on --target across the set of switches --devices

NOTES:
1.
   --find <string> matches all files where <string> is a substring of filename.  For example:

   --find log will match poap_retry_debugs.log, log_profile.yaml, logger.out, etc...
2. -target can be a flash device or a directory of a flash device. For example:

   --target bootflash: (find files matching --find <string> only in the root directory of bootflash:)
   --target bootflash:/.rpmstore/config/etc (find files matching --find <string> only in bootflash:/.rpmstore/config/etc)
'''
our_version = 105
script_name = 'switch_find_files'

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
from nxapi.nxapi_dir import NxapiDir

def get_parser():
    ex_prefix = 'Example: '
    help_target = 'If specified, issue dir <target>.  Else, issue dir bootflash:/'
    help_find = 'Find all files whose name includes the specified string.'
    ex_target = '{} --target bootflash:'.format(ex_prefix)
    ex_find = '{} --find log'.format(ex_prefix)

    title = 'NXAPI: find files whose name contains --find <string> on --target across the set of switches --devices'
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: {}'.format(title),
        parents=[ArgsCookie, ArgsNxapiTools])
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    mandatory.add_argument('--target',
                        dest='target',
                        required=False,
                        default='bootflash:/',
                        help='{} {}'.format(help_target, ex_target))

    mandatory.add_argument('--find',
                        dest='find',
                        required=True,
                        help='{} {}'.format(help_find, ex_find))

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
    d = NxapiDir(vault.nxos_username, vault.nxos_password, ip, log)
    d.nxapi_init(cfg)
    d.target = cfg.target
    d.refresh()

    op = list()
    op.append('Hostname {}'.format(d.hostname))
    op.append('IP: {}'.format(ip))
    op.append('Target: {}'.format(d.target))
    op.append(fmt.format('filename', 'size', 'date'))
    matches = list()
    found = False
    for key in d.files:
        if cfg.find not in d.files[key]['fname']:
            continue
        found = True
        op.append(fmt.format(d.files[key]['fname'], d.files[key]['fsize'], d.files[key]['timestring']))

    if found == True:
        with lock:
            for line in op:
                print(line)
            print(separator)

separator = '-' * 50
print(separator)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '    {:<30} {:>12} {:<20}'

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
    t.join()
