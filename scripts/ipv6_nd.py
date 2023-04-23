#!/usr/bin/env python3
"""
Name: ipv6_nd.py
Description: NXAPI: display ipv6 neighbor info for one or more NX-OS switches

Example output:

% ./ipv6_nd.py --vault hashicorp --devices cvd_leaf_1,cvd_spine_1
ip              hostname             ipv6_addr                      intf_out      time_stamp mac            pref owner     
192.168.11.112  cvd-1211-spine       fe80::2a3:8eff:febf:eaf5       Ethernet1/1   00:00:40   00a3.8ebf.eaf5 50   icmpv6    
192.168.11.102  cvd-1311-leaf        fe80::fa0b:cbff:fea9:51bf      Ethernet1/49  00:00:40   f80b.cba9.51bf 50   icmpv6    
% 

"""
our_version = 104
script_name = "ipv6_nd"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_ipv6_nd import NxapiIpv6Neighbor


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display ipv6 neighbor info for one or more NX-OS switches.",
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


def print_header():
    print(
        fmt.format(
            "ip",
            "hostname",
            "ipv6_addr",
            "intf_out",
            "time_stamp",
            "mac",
            "pref",
            "owner",
        )
    )


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiIpv6Neighbor(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vrf = cfg.vrf
    nx.refresh()
    lines = list()
    for neighbor in nx.info:
        nx.ipv6_addr = neighbor
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                nx.ipv6_addr,
                nx.intf_out,
                nx.time_stamp,
                nx.mac,
                nx.pref,
                nx.owner,
            )
        )
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<20} {:<30} {:<13} {:<10} {:<14} {:<4} {:<10}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
