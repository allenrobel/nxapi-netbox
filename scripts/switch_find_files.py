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

Example output:
% ./switch_find_files.py --vault hashicorp --devices cvd_spine_1,cvd_bgw_4,cvd_leaf_3 --find cfg
--------------------------------------------------
192.268.11.112 - cvd-1211-spine
Target: bootflash:/
    filename                               size date                
    zmi_201.cfg                           29234 Jul 10 18:47:26 2018
    opt_cfg.txt                           29371 Aug 21 18:12:58 2018
--------------------------------------------------
192.268.11.101 - cvd-2112-bgw
Target: bootflash:/
    filename                               size date                
    cfg                                   32431 Feb 20 21:45:29 2020
    netflow.cfg                             817 Aug 03 21:32:56 2020
--------------------------------------------------
192.268.11.104 - cvd-1313-leaf
Target: bootflash:/
    filename                               size date                
    arp.cfg                               16081 Jul 25 23:10:33 2022
--------------------------------------------------
% 

'''
our_version = 107
script_name = 'switch_find_files'

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_dir import NxapiDir

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

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    d = NxapiDir(vault.nxos_username, vault.nxos_password, ip, log)
    d.nxapi_init(cfg)
    d.target = cfg.target
    d.refresh()

    lines = list()
    lines.append('{} - {}'.format(ip, d.hostname))
    lines.append('Target: {}'.format(d.target))
    lines.append(fmt.format('filename', 'size', 'date'))
    for key in d.files:
        if cfg.find not in d.files[key]['fname']:
            continue
        lines.append(fmt.format(d.files[key]['fname'], d.files[key]['fsize'], d.files[key]['timestring']))
    if len(lines) != 0:
        lines.append(separator)
    return lines

separator = '-' * 50
print(separator)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = '    {:<30} {:>12} {:<20}'

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
