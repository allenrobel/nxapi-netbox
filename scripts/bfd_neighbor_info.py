#!/usr/bin/env python3
"""
Name: bfd_neighbor_info.py
Description: NXAPI: display bfd neighbors detail information.
"""
our_version = 107
script_name = "bfd_neighbor_info"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_bfd import NxapiBfdNeighbors

ex_ipv6 = " Example: --ipv6"
help_ipv6 = (
    "If present, show ipv6 bgp neighbor state, else show ipv4 bgp neighbor state."
)


def get_parser():
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: display bfd neighbors detail information.",
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


def get_max_width(d):
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width


def print_header():
    print(fmt.format("ip", "hostname", "interface", "key", "value"))


def format_property(ip, hostname, interface, key, value):
    return fmt.format(ip, hostname, interface, key, value)


def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)


def collect_info(ip, bfd):
    """
    This demonstrates retrieving info from NxapiBfdNeighbors using explicit
    property access.  It's the preferred way if you just want to retrieve a couple
    items.  See also: get_info_from_info_dict() if you want to retrieve ALL items.
    """
    lines = list()
    for local_disc in bfd.info:
        bfd.local_disc = local_disc
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "local_disc", bfd.local_disc)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "header", bfd.header))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "vrf_name", bfd.vrf_name)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "src_ip_addr", bfd.src_ip_addr)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "src_ipv6_addr", bfd.src_ipv6_addr
            )
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "dest_ip_addr", bfd.dest_ip_addr
            )
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "dest_ipv6_addr", bfd.dest_ipv6_addr
            )
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "remote_disc", bfd.remote_disc)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "local_state", bfd.local_state)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "remote_state", bfd.remote_state
            )
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "holddown", bfd.holddown)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "cur_detect_mult", bfd.cur_detect_mult
            )
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "intf", bfd.intf))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "out_str", bfd.out_str)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "echo", bfd.echo))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "echo_tx", bfd.echo_tx)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "local_diag", bfd.local_diag)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "demand", bfd.demand))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "poll", bfd.poll))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "min_tx", bfd.min_tx))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "min_rx", bfd.min_rx))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "local_multi", bfd.local_multi)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "detect_timer", bfd.detect_timer
            )
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "down_count", bfd.down_count)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "tx_interval", bfd.tx_interval)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "rx_count", bfd.rx_count)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "rx_avg", bfd.rx_avg))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "rx_min", bfd.rx_min))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "rx_max", bfd.rx_max))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "last_rx", bfd.last_rx)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "tx_count", bfd.tx_count)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "tx_avg", bfd.tx_avg))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "tx_min", bfd.tx_min))
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "tx_max", bfd.tx_max))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "last_tx", bfd.last_tx)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "app", bfd.app))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "up_time", bfd.up_time)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "version", bfd.version)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "diag", bfd.diag))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "state_bit", bfd.state_bit)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "demand_bit", bfd.demand_bit)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "poll_bit", bfd.poll_bit)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "final_bit", bfd.final_bit)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "multiplier", bfd.multiplier)
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "length", bfd.length))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "my_disc", bfd.my_disc)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "your_disc", bfd.your_disc)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "min_tx_interval", bfd.min_tx_interval
            )
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "req_min_rx", bfd.req_min_rx)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "min_echo_interval", bfd.min_echo_interval
            )
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "host_lc", bfd.host_lc)
        )
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "down_reason", bfd.down_reason)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "no_host_reason", bfd.no_host_reason
            )
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "parent", bfd.parent))
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "per_link_str", bfd.per_link_str
            )
        )
        lines.append(format_property(ip, bfd.hostname, bfd.intf, "auth", bfd.auth))
        lines.append(
            format_property(ip, bfd.hostname, bfd.intf, "auth_bit", bfd.auth_bit)
        )
        lines.append(
            format_property(
                ip, bfd.hostname, bfd.intf, "print_details", bfd.print_details
            )
        )
        lines.append("")
    return lines


def get_info_from_info_dict(bfd, ip):
    """
    bfd.info is a dict containing all bfd information.  It's keyed on local_disc and the values are
    dictionaries containing information for each bfd instance.  See collect_info() in this script
    for how to access individual properties.
    """
    lines = list()
    for key in bfd.info:
        if "local_disc" not in bfd.info[key]:
            log.error(
                "skipping. [local_disc] key not found in dictionary {}".format(
                    bfd.info[key]
                )
            )
            return list()
        local_disc = bfd.info[key]["local_disc"]
        for item in sorted(bfd.info[key]):
            lines.append(
                fmt.format(ip, bfd.hostname, local_disc, item, bfd.info[key][item])
            )
        lines.append("")
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    bfd = NxapiBfdNeighbors(vault.nxos_username, vault.nxos_password, ip, log)
    if cfg.ipv6 == True:
        bfd.ipv6 = True
    bfd.nxapi_init(cfg)
    bfd.refresh()
    lines = get_info_from_info_dict(bfd, ip)
    # collect_info() is another way to retrieve information from NxapiBfdNeighbors()
    # We include it here as an example of pulling a subset of info. Replace
    # get_info_from_info_dict() with collect_info() to test it.
    # lines = collect_info(ip, bfd)
    return lines


cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()
fmt = "{:<15} {:<18} {:<15} {:<20} {:<15}"
print_header()
executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
