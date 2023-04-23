#!/usr/bin/env python3
"""
Name: interface_packet_rates.py
Description: NXAPI: display interface input/output packet rates for a set of interfaces

Example output:

% ./interface_packet_rates.py --vault hashicorp --devices cvd_l2_fanout --interfaces Eth1/17,Eth1/18,Eth1/19           
192.168.11.116  cvd_l2_911         Eth1/17                947283  output packet rate
192.168.11.116  cvd_l2_911         Eth1/17               1689334  input packet rate 
192.168.11.116  cvd_l2_911         Eth1/18               1689206  output packet rate
192.168.11.116  cvd_l2_911         Eth1/18                     0  input packet rate 
192.168.11.116  cvd_l2_911         Eth1/19                947262  output packet rate
192.168.11.116  cvd_l2_911         Eth1/19               2534000  input packet rate 

%
"""
our_version = 108
script_name = "interface_packet_rates"

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

help_interfaces = "Comma-separated list (no spaces) of interfaces to monitor"
ex_interfaces = "Example --interfaces Eth1/1,Eth1/2"


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: monitor interface input/output packet rates for a set of interfaces",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    optional = parser.add_argument_group(title="OPTIONAL SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    mandatory.add_argument(
        "--interfaces",
        dest="interfaces",
        required=True,
        help="{} {}".format(help_interfaces, ex_interfaces),
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + str(our_version)
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


def get_interface_list():
    try:
        return cfg.interfaces.split(",")
    except:
        log.error(
            "exiting. Cannot parse --interfaces {}.  Example usage: --interfaces Eth1/1,Eth1/2".format(
                cfg.interfaces
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


def collect_output(ip, nx):
    lines = list()
    lines.append(
        fmt.format(
            ip,
            nx.hostname,
            nx.interface,
            nx.info["eth_outrate1_pkts"],
            "output packet rate",
        )
    )
    lines.append(
        fmt.format(
            ip,
            nx.hostname,
            nx.interface,
            nx.info["eth_inrate1_pkts"],
            "input packet rate",
        )
    )
    return lines


def worker(device, vault, interfaces):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInterface(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    lines = list()
    for interface in interfaces:
        nx.interface = interface
        result = nx.refresh()
        if not result:
            return
        for line in collect_output(ip, nx):
            lines.append(line)
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
interfaces = get_interface_list()

fmt = "{:<15} {:<18} {:<18} {:>10}  {:<18}"

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault, interfaces]
    futures.append(executor.submit(worker, *args))
print_output(futures)
