#!/usr/bin/env python3
'''
Name: nxapi_ip_route_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: NXAPI: Class containing methods for retrieving inventory information from NXOS devices

This corresponds to the output provided by the following cli:

switch# show inventory | json-pretty 
{
    "TABLE_inv": {
        "ROW_inv": [
            {
                "name": "\"Chassis\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis\"",
                "productid": "N9K-C93180YC-EX",
                "vendorid": "V01",
                "serialnum": "FDO21120U5D"
            },
            {
                "name": "\"Slot 1\"",
                "desc": "\"48x10/25G + 6x40/100G Ethernet Module\"",
                "productid": "N9K-C93180YC-EX",
                "vendorid": "V01",
                "serialnum": "FDO21120U5D"
            },
            {
                "name": "\"Power Supply 1\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Power Supply\"",
                "productid": "NXA-PAC-650W-PI",
                "vendorid": "V02",
                "serialnum": "LIT21133N5X"
            },
            {
                "name": "\"Power Supply 2\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Power Supply\"",
                "productid": "NXA-PAC-650W-PI",
                "vendorid": "V02",
                "serialnum": "LIT21133N7X"
            },
            {
                "name": "\"Fan 1\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Fan Module\"",
                "productid": "NXA-FAN-30CFM-B",
                "vendorid": "V01",
                "serialnum": "N/A"
            },
            {
                "name": "\"Fan 2\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Fan Module\"",
                "productid": "NXA-FAN-30CFM-B",
                "vendorid": "V01",
                "serialnum": "N/A"
            },
            {
                "name": "\"Fan 3\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Fan Module\"",
                "productid": "NXA-FAN-30CFM-B",
                "vendorid": "V01",
                "serialnum": "N/A"
            },
            {
                "name": "\"Fan 4\"",
                "desc": "\"Nexus9000 C93180YC-EX chassis Fan Module\"",
                "productid": "NXA-FAN-30CFM-B",
                "vendorid": "V01",
                "serialnum": "N/A"
            }
        ]
    }
}
switch# 


Example script:

#!/usr/bin/env python3
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_inventory import NxapiInventory

def print_header():
    print(fmt.format('ip', 'hostname', 'serial', 'name', 'product_id', 'description'))

fmt = '{:<15} {:<18} {:<12} {:<15} {:<18} {:<30}'

username = 'admin'
password = 'mypassword'
mgmt_ip = '192.168.1.1'
log = get_logger('mylog', 'INFO', 'DEBUG')
inventory = NxapiInventory(username, password, mgmt_ip, log)
inventory.nxapi_init()
# if argparse is used, pass argparse instance to nxapi_init for control
# over cookie behavior and urllib3 configuration.
#inventory.nxapi_init(<argparse_instance>)

inventory.refresh()
d = inventory.info
for item in d:
    inventory.item = item
    print(fmt.format(
        mgmt_ip,
        inventory.hostname,
        inventory.serialnum,
        inventory.name,
        inventory.productid,
        inventory.desc))


Example script output

scripts % ./test_inventory.py
ip           hostname           serial       name            product_id         description                   
192.168.1.1  cvd-1311-leaf      FDO21120U5D  Chassis         N9K-C93180YC-EX    Nexus9000 C93180YC-EX chassis 
192.168.1.1  cvd-1311-leaf      FDO21120U5D  Slot 1          N9K-C93180YC-EX    48x10/25G + 6x40/100G Ethernet Module
192.168.1.1  cvd-1311-leaf      LIT21133N5X  Power Supply 1  NXA-PAC-650W-PI    Nexus9000 C93180YC-EX chassis Power Supply
192.168.1.1  cvd-1311-leaf      LIT21133N7X  Power Supply 2  NXA-PAC-650W-PI    Nexus9000 C93180YC-EX chassis Power Supply
192.168.1.1  cvd-1311-leaf      N/A          Fan 1           NXA-FAN-30CFM-B    Nexus9000 C93180YC-EX chassis Fan Module
192.168.1.1  cvd-1311-leaf      N/A          Fan 2           NXA-FAN-30CFM-B    Nexus9000 C93180YC-EX chassis Fan Module
192.168.1.1  cvd-1311-leaf      N/A          Fan 3           NXA-FAN-30CFM-B    Nexus9000 C93180YC-EX chassis Fan Module
192.168.1.1  cvd-1311-leaf      N/A          Fan 4           NXA-FAN-30CFM-B    Nexus9000 C93180YC-EX chassis Fan Module
'''
our_version = 105

# standard libraries
import re
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiInventory(NxapiBase):
    '''
    Methods for parsing the JSON below.

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info = dict()
        self.refreshed = False

    def clean_value(self,v):
        v = re.sub("'", '', v)
        v = re.sub('"', '', v)
        return v
    def clean_dict(self, d):
        new_dict = dict()
        for key in d:
            new_key = re.sub("'", '', key)
            new_key = re.sub('"', '', key)
            new_dict[new_key] = self.clean_value(d[key])
        return new_dict

    def make_info_dict(self):
        '''

            {
                "name": "\"Fan 1\"", 
                "desc": "\"Nexus9000 93180YC-EX chassis Fan Module\"", 
                "productid": "NXA-FAN-30CFM-B", 
                "vendorid": "V01", 
                "serialnum": "N/A"
            }, 

        creates self.info, a dict() keyed on inventory item name, with the following structure:
            self.info[name]['name']
            self.info[name]['desc']
            self.info[name]['productid']
            self.info[name]['vendorid']
            self.info[name]['serialnum']

        See main library header for the json that is referenced
        '''
        self._info = dict()
        if self.body_length != 1:
            self.log.error('NxapiInventory.make_info_dict: {} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        _list = self._get_table_row('inv', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            try:
                new_dict = self.clean_dict(_dict)
                _name = new_dict['name']
                self.info[_name] = dict()
                self.info[_name]['name'] = _name
            except:
                self.log.error('NxapiInventory.make_info_dict: exiting. Could not access key [name] in new_dict {}'.format(new_dict))
                exit(1)
            self.info[_name] = new_dict

    def refresh(self):
        self.cli = 'show inventory'
        self.show(self.cli)
        self.make_info_dict()
        self.refreshed = True

    @property
    def info(self):
        return self._info

    @property
    def item(self):
        return self._item
    @item.setter
    def item(self, _x):
        '''item is used as the key into self.info[]'''
        self._item = _x

    @property
    def productid(self):
        try:
            return self.info[self.item]['productid']
        except:
            return 'na'

    @property
    def vendorid(self):
        try:
            return self.info[self.item]['vendorid']
        except:
            return 'na'

    @property
    def serialnum(self):
        try:
            return self.info[self.item]['serialnum']
        except:
            return 'na'

    @property
    def name(self):
        try:
            return self.info[self.item]['name']
        except:
            return 'na'

    @property
    def desc(self):
        try:
            return self.info[self.item]['desc']
        except:
            return 'na'
