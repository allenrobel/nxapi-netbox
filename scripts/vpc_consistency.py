#!/usr/bin/env python3
"""
Name: vpc_consistency.py
Description: NXAPI: display inconsistent vpc parameters

Example output when vpc is consistent:

% ./vpc_consistency.py --vault hashicorp --devices cvd_leaf_2 --interface Po11,Po12
192.168.11.103  cvd-1312-leaf        all 22 global vpc params are consistent
192.168.11.103  cvd-1312-leaf        all 7 vni vpc params are consistent
192.168.11.103  cvd-1312-leaf        all 12 vlans vpc params are consistent
192.168.11.103  cvd-1312-leaf        Po11 all 23 interface vpc port-channel params are consistent
192.168.11.103  cvd-1312-leaf        Po12 all 23 interface vpc port-channel params are consistent
%

Example output when vpc po allowed-vlans are mismatched:

% ./vpc_consistency.py --vault hashicorp --devices cvd_leaf_2 --interface Po11,Po12
192.168.11.103  cvd-1312-leaf        all 22 global vpc params are consistent
192.168.11.103  cvd-1312-leaf        all 7 vni vpc params are consistent
192.168.11.103  cvd-1312-leaf        all 12 vlans vpc params are consistent
192.168.11.103  cvd-1312-leaf        Po11 Allowed VLANs
   vpc-param-type: -
   vpc-param-local-val: 1111-1112
   vpc-param-peer-val: 1111
192.168.11.103  cvd-1312-leaf        Po11 Local suspended VLANs
   vpc-param-type: -
   vpc-param-local-val: 1112
   vpc-param-peer-val: -
192.168.11.103  cvd-1312-leaf        Po12 all 23 interface vpc port-channel params are consistent
% 
"""
our_version = 109
script_name = "vpc_consistency"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_vpc_consistency import (
    NxapiVpcConsistencyGlobal,
    NxapiVpcConsistencyVni,
    NxapiVpcConsistencyVlans,
    NxapiVpcConsistencyInterface,
)


def get_parser():
    help_interfaces = "a comma-separated list (no spaces) of port-channel interfaces to test for vpc consistency"
    help_mismatched_labels = "display labels whose number of comma-separated entries differ from the number of values they refer to"

    ex_interfaces = "Example: --interfaces Po1,Po10"
    ex_mismatched_labels = "Example: --mismatched_labels"

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display inconsistent vpc parameters",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    parser.add_argument(
        "--version", action="version", version="{} v{}".format("%(prog)s", our_version)
    )

    default.add_argument(
        "--mismatched_labels",
        dest="mismatched_labels",
        required=False,
        action="store_true",
        default=False,
        help="{} {}".format(help_mismatched_labels, ex_mismatched_labels),
    )

    default.add_argument(
        "--interfaces",
        dest="interfaces",
        required=False,
        default=None,
        help="{} {}".format(help_interfaces, ex_interfaces),
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


def show_inconsistent_params(ip, nx, interface=None):
    lines = list()
    if nx.error_reason != None:
        log.error("{} {} error: {}".format(tb.sid, nx.hostname, nx.error_reason))
        return lines
    inconsistent_items = nx.inconsistent_params
    if len(inconsistent_items) == 0:
        if interface == None:
            lines.append(
                "{:<15} {:<20} all {} {} vpc params are consistent".format(
                    ip, nx.hostname, len(nx.info), nx.param_type
                )
            )
        else:
            lines.append(
                "{:<15} {:<20} {} all {} {} vpc port-channel params are consistent".format(
                    ip, nx.hostname, interface, len(nx.info), nx.param_type
                )
            )
    else:
        for item in nx.inconsistent_params:
            if interface == None:
                lines.append(
                    "{:<15} {:<20} {}".format(ip, nx.hostname, item["vpc-param-name"])
                )
            else:
                lines.append(
                    "{:<15} {:<20} {} {}".format(
                        ip, nx.hostname, interface, item["vpc-param-name"]
                    )
                )
            for key in item:
                if key == "vpc-param-name":
                    continue
                lines.append("   {}: {}".format(key, item[key]))
    return lines


def show_mismatched_labels(ip, nx):
    lines = list()
    if cfg.mismatched_labels == False:
        return lines
    if len(nx.mismatched_info) > 0:
        for label in nx.mismatched_info:
            lines.append(
                "{:<15} {:<20} vpc-param-name {}".format(ip, nx.hostname, label)
            )
            lines.append("    labels {}".format(nx.mismatched_info[label]["names"]))
            lines.append("    values {}".format(nx.mismatched_info[label]["params"]))
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    lines = list()
    for class_name in [
        NxapiVpcConsistencyGlobal,
        NxapiVpcConsistencyVni,
        NxapiVpcConsistencyVlans,
    ]:
        nx = class_name(vault.nxos_username, vault.nxos_password, ip, log)
        nx.nxapi_init(cfg)
        nx.refresh()
        if nx.error_reason != None:
            lines.append("{} {} error: {}".format(ip, nx.hostname, nx.error_reason))
            return lines
        lines += show_inconsistent_params(ip, nx)
        lines += show_mismatched_labels(ip, nx)

    if cfg.interfaces == None:
        return lines
    for interface in cfg.interfaces.split(","):
        nx = NxapiVpcConsistencyInterface(
            vault.nxos_username, vault.nxos_password, ip, log
        )
        nx.nxapi_init(cfg)
        nx.interface = interface
        nx.refresh()
        lines += show_inconsistent_params(ip, nx, interface)
    return lines


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
