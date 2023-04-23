#!/usr/bin/env python3
"""
Name: vpc_status.py
Description: NXAPI: display vpc parameters

Example output:

% ./vpc_status.py --vault hashicorp --devices cvd_leaf_3,cvd_leaf_4
192.168.11.104  cvd-1313-leaf       : peer status:               peer-ok
192.168.11.104  cvd-1313-leaf       : peer status reason:        SUCCESS
192.168.11.104  cvd-1313-leaf       : peer keepalive status:     peer-alive
192.168.11.104  cvd-1313-leaf       : peer consistency:          consistent
192.168.11.104  cvd-1313-leaf       : peer consistency status:   SUCCESS
192.168.11.104  cvd-1313-leaf       : per vlan peer consistency: consistent
192.168.11.104  cvd-1313-leaf       : type 2 consistency:        consistent
192.168.11.104  cvd-1313-leaf       : type 2 consistency status: SUCCESS
192.168.11.104  cvd-1313-leaf       : role:                      primary
192.168.11.104  cvd-1313-leaf       : delay restore:             Timer is off.(timeout = 150s)
192.168.11.104  cvd-1313-leaf       : delay restore svi:         Timer is off.(timeout = 10s)
192.168.11.104  cvd-1313-leaf       : num vpcs:                  2
--
192.168.11.105  cvd-1314-leaf       : peer status:               peer-ok
192.168.11.105  cvd-1314-leaf       : peer status reason:        SUCCESS
192.168.11.105  cvd-1314-leaf       : peer keepalive status:     peer-alive
192.168.11.105  cvd-1314-leaf       : peer consistency:          consistent
192.168.11.105  cvd-1314-leaf       : peer consistency status:   SUCCESS
192.168.11.105  cvd-1314-leaf       : per vlan peer consistency: consistent
192.168.11.105  cvd-1314-leaf       : type 2 consistency:        consistent
192.168.11.105  cvd-1314-leaf       : type 2 consistency status: SUCCESS
192.168.11.105  cvd-1314-leaf       : role:                      secondary
192.168.11.105  cvd-1314-leaf       : delay restore:             Timer is off.(timeout = 150s)
192.168.11.105  cvd-1314-leaf       : delay restore svi:         Timer is off.(timeout = 10s)
192.168.11.105  cvd-1314-leaf       : num vpcs:                  2
--
% 
"""
our_version = 101
script_name = "vpc_status"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_vpc import NxapiVpcStatus


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display vpc parameters",
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


def get_output(ip, nx):
    lines = list()
    prefix = "{:<15} {:<20}:".format(ip, nx.hostname)
    lines.append("{} peer status:               {}".format(prefix, nx.peer_status))
    lines.append(
        "{} peer status reason:        {}".format(prefix, nx.peer_status_reason)
    )
    lines.append(
        "{} peer keepalive status:     {}".format(prefix, nx.peer_keepalive_status)
    )
    lines.append("{} peer consistency:          {}".format(prefix, nx.peer_consistency))
    lines.append(
        "{} peer consistency status:   {}".format(prefix, nx.peer_consistency_status)
    )
    lines.append(
        "{} per vlan peer consistency: {}".format(prefix, nx.per_vlan_peer_consistency)
    )
    lines.append(
        "{} type 2 consistency:        {}".format(prefix, nx.type_2_consistency)
    )
    lines.append(
        "{} type 2 consistency status: {}".format(prefix, nx.type_2_consistency_status)
    )
    lines.append("{} role:                      {}".format(prefix, nx.role))
    lines.append(
        "{} delay restore:             {}".format(prefix, nx.delay_restore_status)
    )
    lines.append(
        "{} delay restore svi:         {}".format(prefix, nx.delay_restore_svi_status)
    )
    lines.append("{} num vpcs:                  {}".format(prefix, nx.num_of_vpcs))
    lines.append("--")
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiVpcStatus(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    if nx.error_reason != None:
        log.error("{} {} error: {}".format(ip, nx.hostname, nx.error_reason))
        return
    return get_output(ip, nx)


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
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
