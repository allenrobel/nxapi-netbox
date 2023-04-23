#!/usr/bin/env python3
"""
Name: nve_interface.py
Description: NXAPI: display nve interface

Example output (truncated for brevity):

% ./nve_interface.py --vault hashicorp --devices cvd_leaf_1          
ip               hostname          interface        key                          value                           
192.168.11.102  cvd-1311-leaf      nve1             adv-vmac                     Yes                             
192.168.11.102  cvd-1311-leaf      nve1             encap-type                   VXLAN                           
192.168.11.102  cvd-1311-leaf      nve1             fabric-convergence-time      135                             
192.168.11.102  cvd-1311-leaf      nve1             fabric-convergence-time-left 0                               
192.168.11.102  cvd-1311-leaf      nve1             host-reach-mode              Control-Plane      
etc...
%
"""
our_version = 105
script_name = "nve_interface"

import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_nve import NxapiNveInterface


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display nve interface",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    parser.add_argument(
        "--version", action="version", version="{} v{}".format("%(prog)s", our_version)
    )
    return parser.parse_args()


def get_device_list():
    try:
        return cfg.devices.split(",")
    except:
        log.error(
            "exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2".format(
                cfg.devices
            )
        )
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
    for interface in d:
        for key in d[interface]:
            if len(key) > width:
                width = len(key)
            if type(d[interface][key]) != type(dict()):
                continue
            for k in d[interface][key]:
                if len(k) > width:
                    width = len(k)
    return width


def get_header(width):
    return fmt.format("ip", " hostname", "interface", "key", "value", width=width)


def get_output(ip, nve, width):
    lines = list()
    for interface in nve.info:
        for key in sorted(nve.info[interface]):
            value = nve.info[interface][key]
            if type(value) != type(dict()):
                lines.append(
                    fmt.format(ip, nve.hostname, interface, key, value, width=width)
                )
                continue
            for k in value:
                lines.append(
                    fmt.format(ip, nve.hostname, interface, k, value[k], width=width)
                )
    if len(lines) != 0:
        lines.append("")
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiNveInterface(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    width = get_max_key_length(nx.info)
    lines.append(get_header(width))
    for line in get_output(ip, nx, width):
        lines.append(line)
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<18} {:<16} {:<{width}} {:<32}"

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
