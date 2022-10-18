#!/usr/bin/env python3
our_version = 106
script_name = 'rib_summary'
'''
Name: rib_summary.py
Description: NXAPI: display ipv4/ipv6 RIB summary 

Example usage:

All options can be combined.
By default, each option is NOT enabled.  So, using only --vault and --devices will print nothing.
Usage examples:
    --ipv6 --total                                                       - print totals for ipv6 routes and paths
    --ipv6 --total --vrf TENANT1                                         - print totals for ipv6 routes and paths in vrf TENANT1
    --ipv4 --prefixes                                                    - print prefix distribution for ipv4 routes
    --ipv4 --summary --best                                              - print summary for ipv4 best paths
    --ipv6 --summary --backup                                            - print summary for ipv6 backup paths
    --ipv6 --ipv4 --total --summary --backup --best --prefixes --vrf FOO - print everything for vrf FOO

./rib_summary.py --vault hashicorp --ipv4 --ipv6 --total --summary --prefixes --best --backup --devices cvd_leaf_1,cvd_leaf_2

NOTES:

1. If a JSON object is missing from the switch's reply, we silently ignore the object.
   This typically happens for backup routes when backup paths are not configured on 
   the switch.  A debug log is printed though, so if you have log-level set to DEBUG
   for file logging you'll find this in the log. e.g. if the following is configured
   in this script:
   log = get_logger(script_name, cfg.loglevel, 'DEBUG')

   You'll see debug logs similar to:

   DEBUG 1523.256 nxapi_rib_summary.make_backup_paths_dict cvd-switch skipping: unable to find [backup-paths] in _dict {'clientnameuni': 'ospf-UNDERLAY', 'best-paths': 136}
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
from nxapi.nxapi_rib_summary import NxapiRibSummaryIpv4, NxapiRibSummaryIpv6

def get_parser():
    help_backup = 'display backup path routes'
    ex_backup = ' Example: --backup'

    help_best = 'display best path routes'
    ex_best = ' Example: --best'

    help_ipv4 = 'display ipv4 routes'
    ex_ipv4 = ' Example: --ipv4'

    help_ipv6 = 'display ipv6 routes'
    ex_ipv6 = ' Example: --ipv6'

    help_prefixes = 'display prefix summaries'
    ex_prefixes = ' Example: --prefixes'

    help_total = 'display total routes'
    ex_total = ' Example: --total'

    help_summary = 'display summary of routes by route type e.g. am, direct, bgp, etc'
    ex_summary = ' Example: --summary'

    help_vrf = 'vrf in which to query ip route summary info'
    ex_vrf = ' Example: --vrf TENANT_1'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display ipv4/ipv6 RIB summary',
        parents=[ArgsCookie, ArgsNxapiTools])
    optional   = parser.add_argument_group(title='OPTIONAL SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    optional.add_argument('--ipv4',
                         dest='ipv4',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_ipv4, ex_ipv4))

    optional.add_argument('--ipv6',
                         dest='ipv6',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_ipv6, ex_ipv6))

    optional.add_argument('--best',
                         dest='best',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_best, ex_best))

    optional.add_argument('--backup',
                         dest='backup',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_backup, ex_backup))

    optional.add_argument('--total',
                         dest='total',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_total, ex_total))

    optional.add_argument('--summary',
                         dest='summary',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_summary, ex_summary))

    optional.add_argument('--prefixes',
                         dest='prefixes',
                         required=False,
                         action='store_true',
                         default=False,
                         help='{} {}'.format(help_prefixes, ex_prefixes))

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

def print_header_summary():
    print()
    print(fmt_summary.format('ip', 'hostname', 'vrf', 'ver', 'path_type', 'am', 'local', 'direct', 'discard', 'bcast', 'bgp'))

def print_values_summary_best(ip, i):
    if cfg.best == False:
        return
    print(fmt_summary.format(
        ip,
        i.hostname,
        i.vrf,
        i.ip_version,
        'best',
        i.am_best,
        i.local_best,
        i.direct_best,
        i.discard_best,
        i.broadcast_best,
        i.bgp_best))

def print_values_summary_backup(ip, i):
    log.info('got cfg.backup {}'.format(cfg.backup))
    if cfg.backup != False:
        return
    print(fmt_summary.format(
        ip,
        i.hostname,
        i.vrf,
        i.ip_version,
        'backup',
        i.am_backup,
        i.local_backup,
        i.direct_backup,
        i.discard_backup,
        i.broadcast_backup,
        i.bgp_backup))

def print_header_prefixes():
    print()
    print(fmt_prefixes.format('ip', 'hostname', 'vrf', 'ver', 'prefixlen', 'value'))

def print_values_prefixes(ip, i):
    for prefix in i.prefix_list:
        i.prefixlen = prefix
        print(fmt_prefixes.format(ip, i.hostname, i.vrf, i.ip_version, i.prefixlen, i.prefix))

def print_header_total():
    print()
    print(fmt_total.format('ip', 'hostname', 'vrf', 'ver', 'routes' , 'paths'))

def print_values_total(ip, i):
        print(fmt_total.format(ip, i.hostname, i.vrf, i.ip_version, i.routes, i.paths))

def worker_total(ip, i):
    print_values_total(ip, i)

def worker_prefixes(ip, i):
    print_values_prefixes(ip, i)

def worker_summary(ip, i):
    if cfg.best:
        print_values_summary_best(ip, i)
    if cfg.backup:
        print_values_summary_backup(ip, i)

def get_instance_list(ip, vault):
    instances = list()
    if cfg.ipv4:
        instances.append(NxapiRibSummaryIpv4(vault.nxos_username, vault.nxos_password, ip, log))
    if cfg.ipv6:
        instances.append(NxapiRibSummaryIpv6(vault.nxos_username, vault.nxos_password, ip, log))
    return instances

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)

    for i in get_instance_list(ip, vault):
        i.nxapi_init(cfg)
        i.vrf = cfg.vrf
        i.refresh()
        with lock:
            if cfg.total:
                print_header_total()
                worker_total(ip, i)
            if cfg.summary:
                print_header_summary()
                worker_summary(ip, i)
            if cfg.prefixes:
                print_header_prefixes()
                worker_prefixes(ip, i)

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
fmt_summary = '{:<15} {:<25} {:<10} {:>3} {:<9} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7}'
fmt_prefixes = '{:<15} {:<25} {:<10} {:>3} {:<9} {:<5}'
fmt_total = '{:<15} {:<25} {:<10} {:>3} {:<7} {:<7}'

lock = Lock()
for device in devices:
    t = Thread(target=worker, args=(device, vault))
    t.start()
