#!/usr/bin/env python3
"""
Name: vrf.py
Summary: NXAPI: display vrfs

Example output:

(py310) arobel@AROBEL-M-15ZV scripts % ./vrf.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2                                              
ip              hostname           vrf_name        vrf_id vrf_state vrf_reason                    
192.168.11.102  cvd-1311-leaf      default         1      Up        --                            
192.168.11.102  cvd-1311-leaf      management      2      Up        --                            
192.168.11.102  cvd-1311-leaf      v1              3      Up        --                            
192.168.11.102  cvd-1311-leaf      v2              4      Up        --                            

192.168.11.103  cvd-1312-leaf      default         1      Up        --                            
192.168.11.103  cvd-1312-leaf      management      2      Up        --                            
192.168.11.103  cvd-1312-leaf      v1              3      Up        --                            
192.168.11.103  cvd-1312-leaf      v2              4      Up        --                            
%
"""
our_version = 107
script_name = "vrf.py"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_vrf import NxapiVrf


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display vrfs",
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
    print(fmt.format("ip", "hostname", "vrf_name", "vrf_id", "vrf_state", "vrf_reason"))


def get_output(ip, vrf):
    lines = list()
    for vrf_name in sorted(vrf.info):
        lines.append(
            fmt.format(
                ip,
                vrf.hostname,
                vrf.info[vrf_name]["vrf_name"],
                vrf.info[vrf_name]["vrf_id"],
                vrf.info[vrf_name]["vrf_state"],
                vrf.info[vrf_name]["vrf_reason"],
            )
        )
    if len(lines) != 0:
        lines.append("")
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiVrf(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    for line in get_output(ip, nx):
        lines.append(line)
    return lines


fmt = "{:<15} {:<18} {:<15} {:<6} {:<9} {:<30}"
print_header()

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
