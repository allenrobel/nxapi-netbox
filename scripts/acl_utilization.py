#!/usr/bin/env python3
our_version = 109
script_name = 'acl_utilization'
'''
Name: acl_utilization.py
Description: NXAPI display acl utilization

Example output:

% ./acl_utilization.py --vault hashicorp --devices cvd_leaf_1
ip              hostname                min_free module feature                             
192.168.11.102  cvd-1311-leaf                  0      1 egress_cntacl                       
192.168.11.102  cvd-1311-leaf                512      1 egress_dest_info_table              
192.168.11.102  cvd-1311-leaf               1790      1 egress_racl                         
192.168.11.102  cvd-1311-leaf                128      1 egress_sup                          
192.168.11.102  cvd-1311-leaf                  2      1 feature_arp_snoop                   
etc...
%

With --ge

% ./acl_utilization.py --vault hashicorp --devices cvd_leaf_1 --ge 1700
ip              hostname                min_free module feature                             
192.168.11.102  cvd-1311-leaf               1790      1 egress_racl                         
% 

With --type

% ./acl_utilization.py --vault hashicorp --devices cvd_leaf_1 --type min_percent
ip              hostname             min_percent module feature                             
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl                       
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl_all                   
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl_ipv4                  
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl_ipv6                  
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl_mac                   
192.168.11.102  cvd-1311-leaf                0.0      1 egress_cntacl_other                 
192.168.11.102  cvd-1311-leaf                0.0      1 egress_dest_info_table              
192.168.11.102  cvd-1311-leaf               0.11      1 egress_racl                         
etc...
%

With --type max_used --ge 128

(py310) arobel@AROBEL-M-15ZV scripts % ./acl_utilization.py --vault hashicorp --devices cvd_leaf_1 --type max_used --ge 128
ip              hostname                max_used module feature                             
192.168.11.102  cvd-1311-leaf                128      1 egress_sup                          
192.168.11.102  cvd-1311-leaf                128      1 egress_sup_other                    
192.168.11.102  cvd-1311-leaf                450      1 ingress_sup                         
192.168.11.102  cvd-1311-leaf                145      1 ingress_sup_ipv4                    
192.168.11.102  cvd-1311-leaf                180      1 ingress_sup_ipv6                    
(py310) arobel@AROBEL-M-15ZV scripts % 

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
from nxapi_netbox.nxapi.nxapi_system_internal_access_list_resource_utilization import NxapiAccessListResourceUtilization

def get_parser():
    ex_prefix = 'Example:'
    help_type = 'Type of information to retrieve. One of {}'.format(','.join(valid_types))
    help_ge = 'Limit display to entries >= this value.'
    help_le = 'Limit display to entries <= this value.'
    ex_type = '{} --type max_used'.format(ex_prefix)
    ex_ge = '{} --ge 3200'.format(ex_prefix)
    ex_le = '{} --le 80.40'.format(ex_prefix)
    help_modules = 'Comma-separated list of modules/linecards to query.'
    ex_modules = '{} --modules 1,2,3'.format(ex_prefix)

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: retrieve acl utilization information.',
        parents=[ArgsCookie, ArgsNxapiTools])
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')

    default.add_argument('--modules',
                        dest='modules',
                        required=False,
                        default=1,
                        help='(default: %(default)s) ' + help_modules + ex_modules)

    default.add_argument('--ge',
                        dest='ge',
                        required=False,
                        default=0.0,
                        help='(default: %(default)s) ' + help_ge + ex_ge)

    default.add_argument('--le',
                        dest='le',
                        required=False,
                        default=9999999.0,
                        help='(default: %(default)s) ' + help_le + ex_le)

    default.add_argument('--type',
                        dest='type',
                        required=False,
                        default='min_free',
                        help='(default: %(default)s) ' + help_type + ex_type)

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
    if 'all' in cfg.type:
        print('{:<15} {:<20} {:>11} {:>6} {:>8} {:<36}'.format(
            'ip',
            'hostname',
            '{}'.format(cfg.type),
            'module',
            'instance',
            'feature'))
    else:
        print('{:<15} {:<20} {:>11} {:>6} {:<36}'.format(
            'ip',
            'hostname',
            '{}'.format(cfg.type),
            'module',
            'feature'))

def get_item(nx):
    item = -1
    if cfg.type == 'max_used':
        item = nx.max_used
    elif cfg.type == 'min_used':
        item = nx.min_used
    elif cfg.type == 'max_free':
        item = nx.max_free
    elif cfg.type == 'min_free':
        item = nx.min_free
    elif cfg.type == 'max_percent':
        item = nx.max_percent
    elif cfg.type == 'min_percent':
        item = nx.min_percent
    elif cfg.type == 'all_used':
        item = nx.all_used
    elif cfg.type == 'all_free':
        item = nx.all_free
    elif cfg.type == 'all_percent':
        item = nx.all_percent
    if item == -1:
        return None
    if isinstance(item, dict):
        for instance in item:
            if item[instance] == -1:
                return None
    return item

def is_within_threshold(item):
    try:
        if float(item) >= ge_threshold and float(item) <= le_threshold:
            return True
    except:
        log.error('Could not convert item {} to float.  Displaying it regardless.'.format(item))
        return True
    return False

def get_all_type(nx, ip, item):
    lines = list()
    for instance in item:
        if not is_within_threshold(item[instance]):
            continue
        lines.append('{:<15} {:<20} {:>11} {:>6} {:>8} {:<36}'.format(
            ip,
            nx.hostname,
            item[instance],
            nx.module,
            instance,
            nx.feature))
    return lines
def get_max_min_type(nx, ip, item):
    lines = list()
    if not is_within_threshold(item):
        return list()
    lines.append('{:<15} {:<20} {:>11} {:>6} {:<36}'.format(
        ip,
        nx.hostname,
        item,
        nx.module,
        nx.feature))
    return lines
def print_item(nx, ip):
    item = get_item(nx)
    if item == None:
        return list()
    if 'all' in cfg.type:
        return get_all_type(nx, ip, item)
    else:
        return get_max_min_type(nx, ip, item)

def get_items(nx, ip, modules):
    for module in modules:
        nx.module = module
        nx.refresh()
        lines = list()
        for feature in nx.features:
            nx.feature = feature
            lines += print_item(nx, ip)
    return lines
def worker(device, vault, modules):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiAccessListResourceUtilization(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    return get_items(nx, ip, modules)

def get_modules():
    modules = list()
    for item in str(cfg.modules).split(','):
        try:
            modules.append(int(item))
        except:
            log.error('Exiting. Expected int() for module. Got {}'.format(cfg.modules))
            log.error('Usage examples:')
            log.error('    --modules 3')
            log.error('    --modules 1,2,4')
            exit(1)
    return modules

valid_types = list()
valid_types.append('max_free')
valid_types.append('min_free')
valid_types.append('max_percent')
valid_types.append('min_percent')
valid_types.append('max_used')
valid_types.append('min_used')
valid_types.append('all_free')
valid_types.append('all_percent')
valid_types.append('all_used')

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
if cfg.type not in valid_types:
    log.error('Exiting. Invalid type {}.  Expected one of {}'.format(cfg.type, ','.join(valid_types)))
    exit(1)
try:
    ge_threshold = float(str(cfg.ge))
    le_threshold = float(str(cfg.le))
except:
    log.error('Exiting. Could not convert --ge {} or --le {} to float: {}'.format(cfg.ge, cfg.le))
    exit(1)

vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
modules = get_modules()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
print_header()
for device in devices:
    args = [device, vault, modules]
    futures.append(executor.submit(worker, *args))
print_output(futures)
