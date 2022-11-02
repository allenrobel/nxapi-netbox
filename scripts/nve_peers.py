#!/usr/bin/env python3
'''
Name: nve_peers.py
Description: NXAPI: display nve peers
Example output (truncated for brevity):

(py310) arobel@AROBEL-M-15ZV scripts % ./nve_peers.py --vault hashicorp --devices cvd_leaf_1           
ip               hostname          peer             key        value                           
192.168.11.102  cvd-1311-leaf      10.3.0.2         if-name    nve1                            
192.168.11.102  cvd-1311-leaf      10.3.0.2         learn-type CP                              
192.168.11.102  cvd-1311-leaf      10.3.0.2         peer-ip    10.3.0.2                        
192.168.11.102  cvd-1311-leaf      10.3.0.2         peer-state Up                              
192.168.11.102  cvd-1311-leaf      10.3.0.2         router-mac 00a3.8ede.4f27                  
192.168.11.102  cvd-1311-leaf      10.3.0.2         uptime     2d03h                           
-
192.168.11.102  cvd-1311-leaf      10.3.0.3         if-name    nve1                            
192.168.11.102  cvd-1311-leaf      10.3.0.3         learn-type CP                              
etc...
'''
our_version = 105
script_name = 'nve_peers'

import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_nve import NxapiNvePeers

def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display nve interface',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

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

def get_max_key_length(d):
    width = 0
    for peer in d:
        for key in d[peer]:
            if len(key) > width:
                width = len(key)
            if type(d[peer][key]) != type(dict()):
                continue
            for k in d[peer][key]:
                if len(k) > width:
                    width = len(k)
    return width

def get_header(width):
    return fmt.format('ip',' hostname', 'peer', 'key', 'value', width=width)

def get_output(ip, nve, width):
    lines = list()
    for peer in nve.info:
        for key in sorted(nve.info[peer]):
            value = nve.info[peer][key]
            if type(value) != type(dict()):
                lines.append(fmt.format(ip, nve.hostname, peer, key, value, width=width))
                continue
            for k in value:
                lines.append(fmt.format(ip, nve.hostname, peer, k, value[k], width=width))
        lines.append('-')
    if len(lines) != 0:
        lines.append('---')
    return lines

def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiNvePeers(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    width = get_max_key_length(nx.info)
    lines.append(get_header(width))
    for line in get_output(ip, nx, width):
        lines.append(line)
    return lines

fmt = '{:<15} {:<18} {:<16} {:<{width}} {:<32}'

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
