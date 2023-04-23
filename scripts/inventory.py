#!/usr/bin/env python3
"""
Name: inventory.py
Description: NXAPI: display "show inventory" info
"""
script_name = "inventory"
our_version = 102
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_inventory import NxapiInventory


def get_parser():
    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display "show inventory" info',
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    default = parser.add_argument_group(title="OPTIONAL SCRIPT ARGS")
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
        if len(output) > 0:
            print()


def print_header():
    print(fmt.format("ip", "hostname", "serial", "name", "product_id", "description"))


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    i = NxapiInventory(vault.nxos_username, vault.nxos_password, ip, log)
    i.nxapi_init()
    # if argparse is used, pass argparse instance to nxapi_init for control
    # over urllib3 configuration and cookie behavior
    i.nxapi_init(cfg)
    i.refresh()
    d = i.info
    lines = list()
    for item in d:
        i.item = item
        lines.append(
            fmt.format(ip, i.hostname, i.serialnum, i.name, i.productid, i.desc)
        )
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<18} {:<12} {:<15} {:<18} {:<30}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
