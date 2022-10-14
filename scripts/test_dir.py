#!/usr/bin/env python3
from general.log import get_logger
from nxapi.nxapi_dir import NxapiDir

def print_dict(d, hostname):
    width = 20
    for key in sorted(d):
        value = d[key]
        if type(value) != type(dict()):
            print("{:<15} {:<15} {:<{width}}".format(hostname, key, value, width=width))
            continue
        for k in value:
            print("{:<15} {:<15} {:<{width}}".format(hostname, k, value[k], width=width))
    print()

mgmt_ip = '172.22.150.102'
log = get_logger('my_script', 'INFO', 'DEBUG')
d = NxapiDir('admin', 'Cisco!2345', mgmt_ip, log)
d.nxapi_init()
d.refresh()
print_dict(d.files, d.hostname)
