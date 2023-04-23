#!/usr/bin/env python3
"""
Name: ipv6_neighbor_summary.py
Description: NXAPI: display ipv6 neighbor summary

Example output:

% ./ipv6_neighbor_summary.py --vault hashicorp --devices cvd_leaf_1,cvd_spine_1
ip              hostname             vrf        static        dynamic         others          throttle     total       
192.168.11.102  cvd-1311-leaf        default    0             1               0               0            1           
192.168.11.112  cvd-1211-spine       default    0             1               0               0            1           
%
"""
our_version = 103
script_name = "ipv6_neighbor_summary"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_ipv6_neighbor_summary import NxapiIpv6NeighborSummary


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display ipv6 neighbor summary",
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
            "ip", "hostname", "vrf", "static", "dynamic", "others", "throttle", "total"
        )
    )


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiIpv6NeighborSummary(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.vrf = cfg.vrf
    nx.refresh()
    lines = list()
    lines.append(
        fmt.format(
            ip,
            nx.hostname,
            nx.vrf,
            nx.static,
            nx.dynamic,
            nx.others,
            nx.throttle,
            nx.total,
        )
    )
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<20} {:<10} {:<13} {:<15} {:<15} {:<12} {:<12}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
