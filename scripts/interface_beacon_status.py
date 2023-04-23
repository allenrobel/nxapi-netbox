#!/usr/bin/env python3
our_version = 111
"""
Name: interface_beacon_status.py
Description: NXAPI: display interface beacon status

Example output:

Using --interface:

% ./interface_beacon_status.py --vault hashicorp --devices cvd_leaf_1 --interface eth1/49
ip              hostname             interface            state   admin   beacon 
192.168.11.102  cvd-1311-leaf        Ethernet1/49         up      up      on     
% 

Without --interface:

% ./interface_beacon_status.py --vault hashicorp --devices cvd_leaf_1                    
ip              hostname             interface            state   admin   beacon 
192.168.11.102  cvd-1311-leaf        mgmt0                up      up      na     
192.168.11.102  cvd-1311-leaf        Ethernet1/1          down    down    off    
192.168.11.102  cvd-1311-leaf        Ethernet1/2          down    up      off
etc...
%

NOTES:

1. mgmt0 is non-virtual, and currently does not support beacon.  We process it anyway in case it ever does support beacon
"""
script_name = "interface_beacon_status"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_interface import NxapiInterface
from nxapi_netbox.nxapi.nxapi_interface import NxapiInterfaceStatus


def get_parser():
    help_interface = "If present, interface to monitor.  If not present, all interfaces will be monitored."
    help_on = "If present, print only interfaces whose beacon status is on. If not present, print all interface beacon status."

    ex_interface = "Example: --interface Eth1/1"
    ex_on = "Example: --on"

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display interface beacon status",
        parents=[ArgsCookie, ArgsNxapiTools],
    )

    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")

    default.add_argument(
        "--interface",
        dest="interface",
        required=False,
        default=None,
        help="{} {}".format(help_interface, ex_interface),
    )

    default.add_argument(
        "--on",
        dest="on",
        required=False,
        action="store_true",
        default=False,
        help="{} {}".format(help_on, ex_on),
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
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)


def print_header():
    print(fmt.format("ip", "hostname", "interface", "state", "admin", "beacon"))


def collect_output(ip, nx):
    lines = list()
    if cfg.on == True and (nx.eth_beacon == "off" or nx.eth_beacon == "na"):
        return lines
    lines.append(
        fmt.format(
            ip, nx.hostname, nx.interface, nx.state, nx.admin_state, nx.eth_beacon
        )
    )
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)

    s = NxapiInterfaceStatus(vault.nxos_username, vault.nxos_password, ip, log)
    s.nxapi_init(cfg)
    s.interface = cfg.interface
    s.refresh()

    nx = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)

    lines = list()
    for interface in s.info:
        if nx.is_virtual_interface(interface):
            continue
        nx.interface = interface
        nx.refresh()
        lines += collect_output(ip, nx)
    lines.append("--")
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<20} {:<20} {:<7} {:<7} {:<7}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
