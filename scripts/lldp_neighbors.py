#!/usr/bin/env python3
"""
Name: lldp_neighbors.py
Description: NXAPI: display lldp neighbor info for one or more NX-OS switches

Example output:

% ./lldp_neighbors.py --vault hashicorp --devices cvd_leaf_1 
local_name       local_port nbr_name         nbr_port      nbr_mgmt_address
cvd-1311-leaf    mgmt0      mgmt_vlan_150    Ethernet1/47  acf2.c506.bd96 
cvd-1311-leaf    Eth1/11    cvd_911_fanout   Ethernet1/1   192.168.11.116 
cvd-1311-leaf    Eth1/12    cvd_911_fanout   Ethernet1/2   192.168.11.116 
cvd-1311-leaf    Eth1/49    cvd-1211-spine   Ethernet1/1   192.168.11.112 
cvd-1311-leaf    Eth1/50    cvd-1211-spine   Ethernet2/1   192.168.11.112 
cvd-1311-leaf    Eth1/51    cvd-1212-spine   Ethernet1/1   192.168.11.113 
cvd-1311-leaf    Eth1/52    cvd-1212-spine   Ethernet2/1   192.168.11.113 
% 

"""
our_version = 106
script_name = "lldp_neighbors"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_lldp import NxapiLldpNeighbors


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display lldp neighbor info for one or more NX-OS switches.",
        parents=[ArgsCookie, ArgsNxapiTools],
    )

    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")

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
        if len(output) > 0:
            print()


def print_header():
    print(
        fmt.format(
            "ip", "hostname", "local_port", "nbr_name", "nbr_port", "nbr_mgmt_address"
        )
    )


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiLldpNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    for local_port in nx.info:
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                local_port,
                nx.info[local_port]["chassis_id"],
                nx.info[local_port]["port_id"],
                nx.info[local_port]["mgmt_addr"],
            )
        )
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<18} {:<10} {:<16} {:<13} {:<15}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
