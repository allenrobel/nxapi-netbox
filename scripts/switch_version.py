#!/usr/bin/env python3
our_version = 110
script_name = "switch_version"
"""
Name: switch_version.py
Description: NXAPI: display NXOS version information

Example usage:

./switch_version.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2
"""
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
from time import sleep

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_version import NxapiVersion


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display NXOS version information",
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


def print_header():
    print(fmt.format("ip", "hostname", "bios", "nxos_version"))


def get_output(ip, nx):
    lines = list()
    lines.append(fmt.format(ip, nx.hostname, nx.bios_ver_str, nx.nxos_ver_str))
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiVersion(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    return get_output(ip, nx)


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<20} {:<9} {:<32}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
