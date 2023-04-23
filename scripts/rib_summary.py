#!/usr/bin/env python3
our_version = 108
script_name = "rib_summary"
"""
Name: rib_summary.py
Description: NXAPI: display ipv4/ipv6 RIB summary 

Example output:

% ./rib_summary.py --vault hashicorp --devices cvd_leaf_1 --ipv4            

TOTALS 172.22.150.102 cvd-1311-leaf
   vrf        ver routes  paths  
   default      4 84      169    

ROUTE TYPE SUMMARY 172.22.150.102 cvd-1311-leaf
   vrf        ver path_type      am   local  direct discard   bcast     bgp
   default      4 best            4       7       7      -1      11      -1
   default      4 backup         -1      -1      -1      -1      -1      -1

PREFIX SUMMARY 172.22.150.102 cvd-1311-leaf
   vrf        ver prefixlen value
   default      4 8         1    
   default      4 30        48   
   default      4 32        35   

% 

NOTES:

1. If neither --ipv4 nor --ipv6 are provided, the script defaults to --ipv4

2. If a JSON object is missing from the switch's reply, we silently ignore the object.
   This typically happens for backup routes when backup paths are not configured on 
   the switch.  A debug log is printed though, so if you have log-level set to DEBUG
   for file logging you'll find this in the log. e.g. if the following is configured
   in this script:
   log = get_logger(script_name, cfg.loglevel, 'DEBUG')

   You'll see debug logs similar to:

   DEBUG 1523.256 nxapi_rib_summary.make_backup_paths_dict cvd-switch skipping: unable to find [backup-paths] in _dict {'clientnameuni': 'ospf-UNDERLAY', 'best-paths': 136}
"""

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_rib_summary import (
    NxapiRibSummaryIpv4,
    NxapiRibSummaryIpv6,
)


def get_parser():
    help_ipv4 = "display ipv4 routes. can be used together with --ipv6"
    ex_ipv4 = " Example: --ipv4"

    help_ipv6 = "display ipv6 routes. can be used together with --ipv4"
    ex_ipv6 = " Example: --ipv6"

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display ipv4/ipv6 RIB summary",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    optional = parser.add_argument_group(title="OPTIONAL SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    optional.add_argument(
        "--ipv4",
        dest="ipv4",
        required=False,
        action="store_true",
        default=False,
        help="{} {}".format(help_ipv4, ex_ipv4),
    )

    optional.add_argument(
        "--ipv6",
        dest="ipv6",
        required=False,
        action="store_true",
        default=False,
        help="{} {}".format(help_ipv6, ex_ipv6),
    )

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
    # if nothing is printed, display some help
    count = 0
    for future in futures:
        count += len(future.result())
    if count == 0:
        example_usage()
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)
        if len(output) > 0:
            print()


def example_usage():
    print("Usage examples:")
    print("   --ipv6 - print RIB information for ipv6")
    print("   --ipv4 - print RIB information for ipv4")
    exit(0)


# prefixes
def get_header_prefixes():
    return fmt_prefixes.format("vrf", "ver", "prefixlen", "value")


def get_values_prefixes(i):
    lines = list()
    for prefix in i.prefix_list:
        i.prefixlen = prefix
        lines.append(fmt_prefixes.format(i.vrf, i.ip_version, i.prefixlen, i.prefix))
    return lines


def worker_prefixes(i):
    lines = list()
    for line in get_values_prefixes(i):
        lines.append(line)
    return lines


# total
def get_header_total():
    return fmt_total.format("vrf", "ver", "routes", "paths")


def get_values_total(i):
    return fmt_total.format(i.vrf, i.ip_version, i.routes, i.paths)


def worker_total(i):
    lines = list()
    lines.append(get_values_total(i))
    return lines


# summary
def get_values_summary_best(i):
    lines = list()
    lines.append(
        fmt_summary.format(
            i.vrf,
            i.ip_version,
            "best",
            i.am_best,
            i.local_best,
            i.direct_best,
            i.discard_best,
            i.broadcast_best,
            i.bgp_best,
        )
    )
    return lines


def get_values_summary_backup(i):
    lines = list()
    lines.append(
        fmt_summary.format(
            i.vrf,
            i.ip_version,
            "backup",
            i.am_backup,
            i.local_backup,
            i.direct_backup,
            i.discard_backup,
            i.broadcast_backup,
            i.bgp_backup,
        )
    )
    return lines


def get_header_summary():
    return fmt_summary.format(
        "vrf", "ver", "path_type", "am", "local", "direct", "discard", "bcast", "bgp"
    )


def worker_summary(i):
    lines = list()
    for line in get_values_summary_best(i):
        lines.append(line)
    for line in get_values_summary_backup(i):
        lines.append(line)
    return lines


def get_instance_list(ip, vault):
    instances = list()
    if cfg.ipv4:
        instances.append(
            NxapiRibSummaryIpv4(vault.nxos_username, vault.nxos_password, ip, log)
        )
    if cfg.ipv6:
        instances.append(
            NxapiRibSummaryIpv6(vault.nxos_username, vault.nxos_password, ip, log)
        )
    return instances


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    lines = list()
    for i in get_instance_list(ip, vault):
        i.nxapi_init(cfg)
        i.vrf = cfg.vrf
        i.refresh()
        x = worker_total(i)
        if len(x) != 0:
            lines.append("")
            lines.append("TOTALS {} {}".format(ip, i.hostname))
            lines.append(get_header_total())
            for line in x:
                lines.append(line)
        x = worker_summary(i)
        if len(x) != 0:
            lines.append("")
            lines.append("ROUTE TYPE SUMMARY {} {}".format(ip, i.hostname))
            lines.append(get_header_summary())
            for line in x:
                lines.append(line)
        x = worker_prefixes(i)
        if len(x) != 0:
            lines.append("")
            lines.append("PREFIX SUMMARY {} {}".format(ip, i.hostname))
            lines.append(get_header_prefixes())
            for line in x:
                lines.append(line)
    return lines


def verify_args(cfg):
    # Default to ipv4 if no options are present.
    if cfg.ipv4 == False and cfg.ipv6 == False:
        cfg.ipv4 = True


cfg = get_parser()
verify_args(cfg)
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
fmt_summary = "   {:<10} {:>3} {:<9} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7}"
fmt_prefixes = "   {:<10} {:>3} {:<9} {:<5}"
fmt_total = "   {:<10} {:>3} {:<7} {:<7}"

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
