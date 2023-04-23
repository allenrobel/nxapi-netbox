#!/usr/bin/env python3
"""
Name: bgp_neighbor_state.py
Description: NXAPI: display bgp neighbor state for all neighbors

Example usage:

./bgp_neighbor_state.py --vault hashicorp --devices cvd_leaf_1
./nxapi_bgp_neighbor_state_sid.py --vault hashicorp --devices cvd_leaf_1 --ipv6

Example output:

% ./bgp_neighbor_state.py --vault hashicorp --devices cvd_bgw_1,cvd_bgw_3
ip                 hostname             peer        state       remote_as       sourceif up        
192.168.11.110     cvd-1111-bgw         10.100.1.1  Established 65002           Ethernet2/32 true      
192.168.11.110     cvd-1111-bgw         10.100.1.5  Established 65002           Ethernet1/32 true      

192.168.11.100     cvd-2111-bgw         10.100.1.6  Established 65001           Ethernet1/35 true      
192.168.11.100     cvd-2111-bgw         10.100.1.14 Established 65001           Ethernet1/36 true      

%
"""
our_version = 106
script_name = "bgp_neighbor_state"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_bgp_neighbors import (
    NxapiBgpNeighborsIpv4,
    NxapiBgpNeighborsIpv6,
)


def get_parser():
    ex_ipv6 = " Example: --ipv6"
    help_ipv6 = (
        "If present, show ipv6 bgp neighbor state, else show ipv4 bgp neighbor state."
    )

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display bgp neighbor state for all neighbors.",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    mandatory.add_argument(
        "--ipv6",
        dest="ipv6",
        required=False,
        action="store_true",
        default=False,
        help="{} {} {}".format("DEFAULT: %(default)s.", help_ipv6, ex_ipv6),
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


def print_header():
    print(
        fmt.format(
            "ip",
            "hostname",
            "peer",
            "state",
            "remote_as",
            "sourceif",
            "up",
            "resettime",
        )
    )


def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)


def collect_info(ip, bgp):
    lines = list()
    for peer in bgp.peers:
        bgp.peer = peer
        lines.append(
            fmt.format(
                ip,
                bgp.hostname,
                peer,
                bgp.state,
                bgp.remoteas,
                bgp.sourceif,
                bgp.up,
                bgp.resettime,
            )
        )
    lines.append("")
    return lines


def worker(ip, vault):
    ip = get_device_mgmt_ip(nb, device)
    if cfg.ipv6 == True:
        print("worker HERE 1")
        nx = NxapiBgpNeighborsIpv6(vault.nxos_username, vault.nxos_password, ip, log)
    elif cfg.ipv6 == False:
        nx = NxapiBgpNeighborsIpv4(vault.nxos_username, vault.nxos_password, ip, log)
    else:
        log.error("Exiting. unknown value for --ipv6")
        exit(1)
    nx.nxapi_init(cfg)
    nx.refresh()
    return collect_info(ip, nx)


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<18} {:<20} {:<11} {:<11} {:<15} {:<5} {:<10}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
