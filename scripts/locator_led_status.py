#!/usr/bin/env python3
"""
Name: locator_led_status.py
Description: NXAPI: display locator-led status for chassis, modules, fans

Example output:

% ./locator_led_status.py --vault hashicorp --devices cvd_bgw_1 --module 1,2 --fan 1,2
ip              hostname           status locator-led 
192.168.11.110  cvd-1111-bgw       ON     chassis     
192.168.11.110  cvd-1111-bgw       OFF    module_1    
192.168.11.110  cvd-1111-bgw       ON     module_2    
192.168.11.110  cvd-1111-bgw       ON     fan_1       
192.168.11.110  cvd-1111-bgw       OFF    fan_2       

%
"""
our_version = 106
script_name = "locator_led_status"

# standard libraries
import argparse
import re
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_locator_led import NxapiLocatorLedStatus


def get_parser():
    ex_prefix = "Example:"
    help_module = (
        "Either a single module/linecard, or a comma-separate list of modules/linecards"
    )
    help_fan = "Either a single fan, or a comma-separate list of fans"
    help_on = "If present, print only locator-leds whose status is ON. If not present, print status for all locator-leds"
    ex_module = "{} --module 2,3,6".format(ex_prefix)
    ex_fan = "{} --fan 3".format(ex_prefix)
    ex_on = "{} --on".format(ex_prefix)

    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display locator-led status for chassis, modules, fans",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")
    optional = parser.add_argument_group(title="OPTIONAL SCRIPT ARGS")

    optional.add_argument(
        "--on",
        dest="on",
        required=False,
        action="store_true",
        default=False,
        help="{} {}".format(help_on, ex_on),
    )
    optional.add_argument(
        "--module",
        dest="module",
        required=False,
        default=None,
        help="(default: %(default)s) " + help_module + ex_module,
    )
    optional.add_argument(
        "--fan",
        dest="fan",
        required=False,
        default=None,
        help="(default: %(default)s) " + help_fan + ex_fan,
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
        if len(output) > 0:
            print()


def print_header():
    print(fmt.format("ip", "hostname", "status", "locator-led"))


def collect_output(ip, nx, modules, fans):
    lines = list()
    if not cfg.on:
        lines.append(fmt.format(ip, nx.hostname, nx.chassis, "chassis"))
    elif cfg.on and nx.chassis == "ON":
        lines.append(fmt.format(ip, nx.hostname, nx.chassis, "chassis"))
    for module in modules:
        nx.module = module
        if cfg.on and nx.module_status != "ON":
            continue
        lines.append(
            fmt.format(ip, nx.hostname, nx.module_status, "module_{}".format(module))
        )
    for fan in fans:
        nx.fan = fan
        if cfg.on and nx.fan_status != "ON":
            continue
        lines.append(fmt.format(ip, nx.hostname, nx.fan_status, "fan_{}".format(fan)))
    return lines


def worker(device, vault, modules, fans):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiLocatorLedStatus(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    return collect_output(ip, nx, modules, fans)


def cfg_to_list(cfg_list, desc):
    _list = list()
    if cfg_list == None:
        return _list
    for item in re.split(",", str(cfg_list)):
        if item == None:
            continue
        try:
            _list.append(int(item))
        except:
            log.error("Exiting. Expected int() for {}. Got {}".format(desc, cfg_list))
            log.error("Usage examples:")
            log.error("    --{} 3".format(desc))
            log.error("    --{} 1,2,4".format(desc))
            exit(1)
    return _list


cfg = get_parser()
modules = cfg_to_list(cfg.module, "module")
fans = cfg_to_list(cfg.fan, "fan")
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt = "{:<15} {:<18} {:<6} {:<12}"
print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault, modules, fans]
    futures.append(executor.submit(worker, *args))
print_output(futures)
