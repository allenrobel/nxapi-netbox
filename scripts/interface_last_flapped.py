#!/usr/bin/env python3
"""
Name: interface_last_flapped.py
Description: NXAPI: display interface last flapped/cleared timers, and reset info

flapped and cleared timers are converted to seconds.

Example usage:

% ./interface_last_flapped.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2 --interface Eth1/49,Eth1/50,Eth1/51,Eth1/52
ip              hostname           interface       state   admin   flapped   cleared   resets
192.168.11.102  cvd-1311-leaf      Ethernet1/49    up      up      5818.0    1045.0    0     
192.168.11.102  cvd-1311-leaf      Ethernet1/50    up      up      151200.0  151200.0  4     
192.168.11.102  cvd-1311-leaf      Ethernet1/51    up      up      151200.0  151200.0  4     
192.168.11.102  cvd-1311-leaf      Ethernet1/52    up      up      151200.0  151200.0  4     

192.168.11.103  cvd-1312-leaf      Ethernet1/49    up      up      151200.0  151200.0  4     
192.168.11.103  cvd-1312-leaf      Ethernet1/50    up      up      151200.0  151200.0  4     
192.168.11.103  cvd-1312-leaf      Ethernet1/51    up      up      151200.0  151200.0  4     
192.168.11.103  cvd-1312-leaf      Ethernet1/52    up      up      151200.0  151200.0  4     

% 
"""
our_version = 106
script_name = "interface_last_flapped"

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
    ex_interface = "Example: --interface Eth1/1"

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display interface last flapped/cleared timers, and reset info",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    optional = parser.add_argument_group(title="OPTIONAL SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    optional.add_argument(
        "--interface",
        dest="interface",
        required=False,
        default=None,
        help="{} {}".format(help_interface, ex_interface),
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


def get_max_width(d):
    """
    not used
    """
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width


def print_header():
    print(
        fmt.format(
            "ip",
            "hostname",
            "interface",
            "state",
            "admin",
            "flapped",
            "cleared",
            "resets",
        )
    )


def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)
        if len(output) > 0:
            print()


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)

    i = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init(cfg)

    # used to get the list of interfaces from s.info
    s = NxapiInterfaceStatus(vault.nxos_username, vault.nxos_password, ip, log)
    s.nxapi_init(cfg)
    s.interface = cfg.interface
    s.refresh()
    lines = list()
    for interface in s.info:
        i.interface = interface
        i.refresh()
        lines.append(
            fmt.format(
                ip,
                i.hostname,
                i.interface,
                i.state,
                i.admin_state,
                i.eth_link_flapped,
                i.eth_clear_counters,
                i.eth_reset_cntr,
            )
        )
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<18} {:<15} {:<7} {:<7} {:<9} {:<9} {:<6}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
