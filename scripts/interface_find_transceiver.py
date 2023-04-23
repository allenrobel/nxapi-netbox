#!/usr/bin/env python3
"""
Name: interface_find_transceiver.py
Description: NXAPI: Find transceivers across one or more switches, using a variety of search terms

Example output:

Searching for substring in --name:

% ./interface_find_transceiver.py --vault hashicorp --devices cvd_leaf_1 --name CISCO 
ip              hostname             interface            serial_num           search_term value
192.168.11.102  cvd-1311-leaf        Ethernet1/9          APF20170506-CH1      name        CISCO-AMPHENOL
192.168.11.102  cvd-1311-leaf        Ethernet1/11         A4Z2103K1Y9-B        name        CISCO-AVAGO
192.168.11.102  cvd-1311-leaf        Ethernet1/12         A4Z2103K1Y7-A        name        CISCO-AVAGO
192.168.11.102  cvd-1311-leaf        Ethernet1/49         FIW202102SX-B        name        CISCO-FINISAR
etc...
%

Searching multiple switches for substring in --serialnum

% ./interface_find_transceiver.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_leaf_3,cvd_leaf_4 --serialnum FIW2229030N     
ip              hostname             interface            serial_num           search_term value
192.168.11.104  cvd-1313-leaf        Ethernet1/11         FIW2229030N-A        serialnum   FIW2229030N-A
--
% 

Searching for substring in --type

% ./interface_find_transceiver.py --vault hashicorp --devices cvd_leaf_1 --type 100G
ip              hostname             interface            serial_num           search_term value
192.168.11.102  cvd-1311-leaf        Ethernet1/49         FIW202102SX-B        type        QSFP-100G-AOC1M
192.168.11.102  cvd-1311-leaf        Ethernet1/50         FIW202003MS-B        type        QSFP-100G-AOC1M
192.168.11.102  cvd-1311-leaf        Ethernet1/51         FIW202102TE-A        type        QSFP-100G-AOC1M
192.168.11.102  cvd-1311-leaf        Ethernet1/52         FIW202005PW-B        type        QSFP-100G-AOC1M
--
scripts % 
"""
our_version = 102
script_name = "interface_find_transceiver"

# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor

# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_interface_transceiver import NxapiInterfaceTransceiver


def get_parser():
    help_ciscoid = "str() Search for substring in ciscoid"
    help_ciscoid_1 = "str() Search for substring in ciscoid_1"
    help_cisco_part_number = "str() Search for substring in cisco_part_number"
    help_cisco_product_id = "str() Search for substring in cisco_product_id"
    help_cisco_vendor_id = "str() Search for substring in cisco_vendor_id"
    help_name = "str() Search for substring in name"
    help_nom_bitrate = "int() Search for bitrate <= nom_bitrate"
    help_partnum = "str() Search for substring in partnum"
    help_rev = "str() Search for substring in rev"
    help_serialnum = "str() Search for substring in serialnum"
    help_type = "str() Search for substring in type"
    ex = "Example: "
    ex_ciscoid = "{} --ciscoid 17"
    ex_ciscoid_1 = "{} --ciscoid_1 220"
    ex_cisco_part_number = "{} --cisco_part_number 10-3172-01"
    ex_cisco_product_id = "{} --cisco_product_id QSFP"
    ex_cisco_vendor_id = "{} --cisco_vendor_id V01"
    ex_name = "{} --name FINISAR"
    ex_nom_bitrate = "{} --nom_bitrate 25500"
    ex_partnum = "{} --partnum FTCL4352RH"
    ex_rev = "{} --rev D"
    ex_serialnum = "{} --serialnum FIW201014ZC"
    ex_type = "{} --type QSFP"
    parser = argparse.ArgumentParser(
        description="DESCRIPTION: NXAPI: Find transceivers across one or more switches, using a variety of search terms",
        parents=[ArgsCookie, ArgsNxapiTools],
    )
    default = parser.add_argument_group(title="DEFAULT SCRIPT ARGS")
    mandatory = parser.add_argument_group(title="MANDATORY SCRIPT ARGS")

    # Below, we set default to a string that is very unlikely to appear as a value
    # for any field in 'show interface transceiver'.  This needs to be a str(),
    # rather than bool() or none() since we are checking if it's a substring of
    # the field value.
    default.add_argument(
        "--ciscoid",
        dest="ciscoid",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_ciscoid, ex_ciscoid),
    )
    default.add_argument(
        "--ciscoid_1",
        dest="ciscoid_1",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_ciscoid_1, ex_ciscoid_1),
    )
    default.add_argument(
        "--cisco_part_number",
        dest="cisco_part_number",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_cisco_part_number, ex_cisco_part_number),
    )
    default.add_argument(
        "--cisco_product_id",
        dest="cisco_product_id",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_cisco_product_id, ex_cisco_product_id),
    )
    default.add_argument(
        "--cisco_vendor_id",
        dest="cisco_vendor_id",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_cisco_vendor_id, ex_cisco_vendor_id),
    )
    default.add_argument(
        "--name",
        dest="name",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_name, ex_name),
    )
    default.add_argument(
        "--nom_bitrate",
        dest="nom_bitrate",
        required=False,
        default=-1,
        help="{} {}".format(help_nom_bitrate, ex_nom_bitrate),
    )
    default.add_argument(
        "--partnum",
        dest="partnum",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_partnum, ex_partnum),
    )
    default.add_argument(
        "--rev",
        dest="rev",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_rev, ex_rev),
    )
    default.add_argument(
        "--serialnum",
        dest="serialnum",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_serialnum, ex_serialnum),
    )
    default.add_argument(
        "--type",
        dest="type",
        required=False,
        default="xxxxxxxxxxxxxxxx",
        help="{} {}".format(help_type, ex_type),
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


def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)


def print_header():
    print(
        fmt.format("ip", "hostname", "interface", "serial_num", "search_term", "value")
    )


def search(ip, nx):
    lines = list()
    if cfg.ciscoid in nx.ciscoid:
        lines.append(
            fmt.format(
                ip, nx.hostname, nx.interface, nx.serialnum, "ciscoid", nx.ciscoid
            )
        )
    if cfg.ciscoid_1 in nx.ciscoid_1:
        lines.append(
            fmt.format(
                ip, nx.hostname, nx.interface, nx.serialnum, "ciscoid_1", nx.ciscoid_1
            )
        )
    if cfg.cisco_part_number in nx.cisco_part_number:
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                nx.interface,
                nx.serialnum,
                "cisco_part_num",
                nx.cisco_part_number,
            )
        )
    if cfg.cisco_product_id in nx.cisco_product_id:
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                nx.interface,
                nx.serialnum,
                "product_id",
                nx.cisco_product_id,
            )
        )
    if cfg.cisco_vendor_id in nx.cisco_vendor_id:
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                nx.interface,
                nx.serialnum,
                "vendor_id",
                nx.cisco_vendor_id,
            )
        )
    if cfg.name in nx.name:
        lines.append(
            fmt.format(ip, nx.hostname, nx.interface, nx.serialnum, "name", nx.name)
        )
    try:
        cfg_nom_bitrate = int(cfg.nom_bitrate)
    except:
        log.error(
            "exiting. expected int() for --nom_bitrate, got {}".format(cfg.nom_bitrate)
        )
        exit(1)
    if cfg_nom_bitrate >= nx.nom_bitrate:
        lines.append(
            fmt.format(
                ip,
                nx.hostname,
                nx.interface,
                nx.serialnum,
                "nom_bitrate",
                nx.nom_bitrate,
            )
        )
    if cfg.partnum in nx.partnum:
        lines.append(
            fmt.format(
                ip, nx.hostname, nx.interface, nx.serialnum, "partnum", nx.partnum
            )
        )
    if cfg.rev in nx.rev:
        lines.append(
            fmt.format(ip, nx.hostname, nx.interface, nx.serialnum, "rev", nx.rev)
        )
    if cfg.serialnum in nx.serialnum:
        lines.append(
            fmt.format(
                ip, nx.hostname, nx.interface, nx.serialnum, "serialnum", nx.serialnum
            )
        )
    if cfg.type in nx.sfp_type:
        lines.append(
            fmt.format(ip, nx.hostname, nx.interface, nx.serialnum, "type", nx.sfp_type)
        )
    return lines


def find_transceivers(ip, nx):
    lines = list()
    for interface in nx.interfaces:
        nx.interface = interface
        lines += search(ip, nx)
    return lines


def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiInterfaceTransceiver(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = find_transceivers(ip, nx)
    if len(lines) > 0:
        lines.append("--")
    return lines


fmt = "{:<15} {:<20} {:<20} {:<20} {:<11} {}"

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, "DEBUG")
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

print_header()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    futures.append(executor.submit(worker, *args))
print_output(futures)
