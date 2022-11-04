#!/usr/bin/env python3
'''
Name: system_process_memory.py
Description: NXAPI: display memory usage of system processes

This script displays cumulative memory usage for physical, virtual, and rss memory for each process name.

Some processes (e.g. bash) contain multiple entries with the same name.  For these,
we sum their memory usage and print a list of process IDs with this name.

Example output:

Without --summed:

% ./system_process_memory.py --vault hashicorp --devices cvd_leaf_1
ip              hostname           process_name              virtual  physical rss      processid(s)
192.168.11.102  cvd-1311-leaf      init                      2272     141      1680     1
192.168.11.102  cvd-1311-leaf      vsh.bin                   694232   21068    102096   3794
192.168.11.102  cvd-1311-leaf      vsh.bin                   694028   18354    95652    6173
192.168.11.102  cvd-1311-leaf      sleep                     2268     123      1348     6210
192.168.11.102  cvd-1311-leaf      vsh.bin                   693084   11625    88416    6214
192.168.11.102  cvd-1311-leaf      rpcbind                   2808     285      1752     8419
etc...

With --summed:

% ./system_process_memory.py --vault hashicorp --devices cvd_leaf_1 --summed 
ip              hostname           process_name              virtual  physical rss      instances processid(s)
192.168.11.102  cvd-1311-leaf      aaad                      485172   14729    63680    1         22079
192.168.11.102  cvd-1311-leaf      acllog                    469552   12360    58384    1         25528
192.168.11.102  cvd-1311-leaf      aclmgr                    492344   20832    73484    1         22333
192.168.11.102  cvd-1311-leaf      aclqos                    1165052  87291    331920   2         25598,27514
192.168.11.102  cvd-1311-leaf      adbm                      403108   10711    52284    1         25527
192.168.11.102  cvd-1311-leaf      agetty                    42940    1446     8636     5         24767,24770,24771,24774,24776
etc...

Comparing process memory usage for one process across multiple switches:

% ./system_process_memory.py --vault hashicorp --devices cvd_leaf_1,cvd_leaf_2,cvd_leaf_3,cvd_leaf_4 --processname vsh.bin --summed
ip              hostname           process_name              virtual  physical rss      instances processid(s)
192.168.11.102  cvd-1311-leaf      vsh.bin                   8001232  164588   954144   12        12780,13510,13663,14907,24368,24369,24371,24376,26701,26727,26739,27047
192.168.11.103  cvd-1312-leaf      vsh.bin                   5624604  132032   780888   8         15130,15131,15133,15136,25563,26476,26563,27963
192.168.11.104  cvd-1313-leaf      vsh.bin                   5496848  128874   729872   8         8856,8857,8859,8861,16761,17548,18574,19092
192.168.11.105  cvd-1314-leaf      vsh.bin                   6190788  141882   825896   9         2115,2116,2118,2120,14086,14870,15700,15740,16401
 % 
'''
# standard libraries
import argparse
from concurrent.futures import ThreadPoolExecutor
# local libraries
from nxapi_netbox.args.args_cookie import ArgsCookie
from nxapi_netbox.args.args_nxapi_tools import ArgsNxapiTools
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.netbox.netbox_session import netbox, get_device_mgmt_ip
from nxapi_netbox.vault.vault import get_vault
from nxapi_netbox.nxapi.nxapi_process_memory import NxapiProcessMemoryPhysical

our_version = 100
script_name = 'system_process_memory'

def get_parser():
    help_summed = 'By default, processes are individually listed, by processid.  If --summed is present, then memory usage for processes with the same processname are summed and entry for the process name is printed, along with a list of processids for that name.'
    help_processname = 'If present, retrieve stats only for this process.'

    ex_summed = 'Example: --summed'
    ex_processname = 'Example: --processname dcos_sshd'

    parser = argparse.ArgumentParser(
        description='DESCRIPTION: NXAPI: display memory usage of system processes',
        parents=[ArgsCookie, ArgsNxapiTools])
    default   = parser.add_argument_group(title='DEFAULT SCRIPT ARGS')
    mandatory = parser.add_argument_group(title='MANDATORY SCRIPT ARGS')

    default.add_argument('--summed',
                        dest='summed',
                        required=False,
                        action='store_true',
                        default=False,
                        help='{} {} {}'.format('DEFAULT: %(default)s.', help_summed, ex_summed))

    default.add_argument('--processname',
                        dest='processname',
                        required=False,
                        default=None,
                        help='{} {} {}'.format('DEFAULT: %(default)s.', help_processname, ex_processname))

    parser.add_argument('--version',
                        action='version',
                        version='{} v{}'.format('%(prog)s', our_version))
    return parser.parse_args()

def get_device_list():
    try:
        return cfg.devices.split(',')
    except:
        log.error('exiting. Cannot parse --devices {}.  Example usage: --devices leaf_1,spine_2,leaf_2'.format(cfg.devices))
        exit(1)

def print_output(futures):
    for future in futures:
        output = future.result()
        if output == None:
            continue
        for line in output:
            print(line)

def print_header_worker():
    print(fmt_worker.format('ip', 'hostname', 'process_name', 'virtual', 'physical', 'rss', 'instances', 'processid(s)'))
def print_header_worker_by_processid():
    print(fmt_worker_by_processid.format('ip', 'hostname', 'process_name', 'virtual', 'physical', 'rss', 'processid'))

# Use this to view individual memory stats for all processes
def worker_by_processid(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiProcessMemoryPhysical(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    if cfg.processname != None:
        for process_id in nx.info_by_processid:
            processname = nx.info_by_processid[process_id]['processname']
            if processname == cfg.processname:
                physical = nx.info_by_processid[process_id]['physical']
                rss = nx.info_by_processid[process_id]['rss']
                virtual = nx.info_by_processid[process_id]['virtual']
                lines.append(fmt_worker_by_processid.format(ip, nx.hostname, processname, virtual, physical, rss, process_id))
    else:
        for process_id in nx.info_by_processid:
            processname = nx.info_by_processid[process_id]['processname']
            physical = nx.info_by_processid[process_id]['physical']
            rss = nx.info_by_processid[process_id]['rss']
            virtual = nx.info_by_processid[process_id]['virtual']
            lines.append(fmt_worker_by_processid.format(ip, nx.hostname, processname, virtual, physical, rss, process_id))
    return lines

# Use this to view summed memory stats for processes with the same name
def worker(device, vault):
    ip = get_device_mgmt_ip(nb, device)
    nx = NxapiProcessMemoryPhysical(vault.nxos_username, vault.nxos_password, ip, log)
    nx.nxapi_init(cfg)
    nx.refresh()
    lines = list()
    if cfg.processname != None:
        nx.process = cfg.processname
        lines.append(fmt_worker.format(ip, nx.hostname, nx.processname, nx.virtual, nx.physical, nx.rss, nx.instances, nx.processid))
    else:
        for process in nx.process_names:
            nx.process = process
            lines.append(fmt_worker.format(ip, nx.hostname, nx.processname, nx.virtual, nx.physical, nx.rss, nx.instances, nx.processid))
    return lines

cfg = get_parser()
log = get_logger(script_name, cfg.loglevel, 'DEBUG')
vault = get_vault(cfg.vault)
vault.fetch_data()
nb = netbox(vault)

devices = get_device_list()

fmt_worker = '{:<15} {:<18} {:<25} {:<8} {:<8} {:<8} {:<9} {}'
fmt_worker_by_processid = '{:<15} {:<18} {:<25} {:<8} {:<8} {:<8} {}'
if cfg.summed == True:
    print_header_worker()
else:
    print_header_worker_by_processid()

executor = ThreadPoolExecutor(max_workers=len(devices))
futures = list()
for device in devices:
    args = [device, vault]
    if cfg.summed == True:
        futures.append(executor.submit(worker, *args))
    else:
        futures.append(executor.submit(worker_by_processid, *args))

print_output(futures)
