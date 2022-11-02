#!/usr/bin/env python3
'''
Name: nxapi_mac_address_table.py
Author: Allen Robel (arobel@cisco.com)
Description: Class containing methods for retrieving mac address-table information via NXAPI

NxapiMacCount() corresponds to the output provided by the following cli:

show mac address-table count

switch# show mac address-table count | json-pretty
{
    "TABLE-macaddtblcount": {
        "id-out": "0", 
        "count_str": "MAC Entries for all vlans :", 
        "total_cnt": "95139", 
        "dyn_cnt": "63424", 
        "otv_cnt": "31713", 
        "static_cnt": "2", 
        "secure_cnt": "0"
    }
}
switch# 

Synopsis:

from nxapi_netbox.nxapi.nxapi_mac_address_table import NxapiMacCount
from nxapi_netbox.general.log import get_logger

console_loglevel = 'INFO'
file_loglevel = 'DEBUG'
log = get_logger('my_script_name', console_loglevel, file_loglevel)

ip = '192.168.1.1'
nx = NxapiMacCount('myusername', 'mypassword', ip, log)
# nxapi_init() can take an argparse instance to disable cookies. By default, cookies are enabled.
# see ~/lib/general/args_cookie.py for details
nx.nxapi_init()

# without setting nx.vlan, mac count for all vlans is displayed
nx.refresh()
fmt = '{:<15} {:<18} {:>4} {:>7} {:>7} {:>7} {:>5} {:>7} {:>7}'
print(fmt.format('ip', 'device', 'vlan', 'total', 'dyn', 'otv', 'rvtep', 'static', 'secure'))
print(fmt.format(
    nx.hostname,
    nx.total_cnt,
    nx.dyn_cnt,
    nx.otv_cnt,
    nx.rvtep_static_cnt,
    nx.static_cnt,
    nx.secure_cnt))

# set nx.vlan to display mac address count only in vlan 10
nx.vlan = 10
nx.refresh()
print(fmt.format('ip', 'device', 'vlan', 'total', 'dyn', 'otv', 'rvtep', 'static', 'secure'))
print(fmt.format(
    mac.hostname,
    mac.total_cnt,
    mac.dyn_cnt,
    mac.otv_cnt,
    nx.rvtep_static_cnt,
    mac.static_cnt,
    mac.secure_cnt))
'''
our_version = 110

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiMacCount(NxapiBase):
    '''
    Methods for parsing the JSON below.

        {
            "TABLE-macaddtblcount": {
                "id-out": "0",
                "count_str": "MAC Entries for all vlans :",
                "dyn_cnt": "0",
                "otv_cnt": "0",
                "rvtep_static_cnt": "0",
                "static_cnt": "0",
                "secure_cnt": "0",
                "total_cnt": "0"
            }
        }


    Creates a 1-level dictionary with the same keys as shown above (except id-out is converted to id_out)

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.class_name = 'NxapiMacCount'
        self.timeout = 20
        self._vlan = 0

    def make_info_dict(self):
        '''
        from self.body[0] populate self.info dict(),

        NOTE: data structure changed between 7.0(3)I6(1) and 7.0(3)I7(2).  See below.

        For backward-compatibility, we warn about pre-7.0(3)I7(2) accesses.

        7.0(3)I6(1)
        {
            "TABLE-macaddtblcount": {
                "dyn_cnt": "43604", 
                "otv_cnt": "0", 
                "static_cnt": "0", 
                "secure_cnt": "0"
            }
        }

        7.0(3)I7(2)
        {
            "TABLE-macaddtblcount": {
                "id-out": "0", 
                "count_str": "MAC Entries for all vlans :", 
                "dyn_cnt": "0", 
                "otv_cnt": "0", 
                "static_cnt": "0", 
                "secure_cnt": "0"
                "total_cnt": "0",
            }
        }

        9.3(2)
        {
            "TABLE-macaddtblcount": {
                "id-out": "0",
                "count_str": "MAC Entries for all vlans :",
                "dyn_cnt": "0",
                "otv_cnt": "0",
                "rvtep_static_cnt": "0",  <--- new
                "static_cnt": "0",
                "secure_cnt": "0",
                "total_cnt": "0"
            }
        }

        '''
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return

        try:
            self.log.debug('{} {} self.body[0] {}'.format(self.class_name, self.hostname, self.body[0]))
            _dict = self.body[0]['TABLE-macaddtblcount']
        except:
            self.log.warning('{} early return: maybe self.vlan set to vlan that does not exist?  Unable to find TABLE-macaddtblcount in {}'.format(self.hostname, self.body[0]))
            return

        # backward compatibility hacks
        # pre-7.0(3)I7(2)
        if 'total_cnt' not in _dict:
            total_cnt = 0
            _cnt_keys = list()
            for _key in _dict:
                # this assumes all keys worth counting are of the format label_cnt
                if '_cnt' in _key:
                    _cnt_keys.append(_key)
                    total_cnt += int(_dict[_key])
            self.log.warning('{} pre-7.0(3)I7(2). Synthesized value for total_cnt as: {}'.format(self.hostname, ' + '.join(_cnt_keys)))
            _dict['total_cnt'] = total_cnt

        # rvtep_static_cnt was introduced in 9.3(2)
        # For prior images, add it with a value of zero
        if 'rvtep_static_cnt' not in _dict:
            _dict['rvtep_static_cnt'] = 0
        self.info = _dict


    def print_dict(self):
        '''
        print the contents of self.info
        '''
        for key in self.info:
            self.log.info('{} self.info[{}] = {}'.format(self.hostname, key, self.info[key]))

    def refresh(self):
        if self.vlan == 0:
            self.cli = 'show mac address-table count'
        else:
            self.cli = 'show mac address-table count vlan {}'.format(self.vlan)
        self.show()
        self.make_info_dict()
 
    @property
    def vlan(self):
        return self._vlan
    @vlan.setter
    def vlan(self, _x):
        if not self.verify.is_digits(_x):
            self.log.error('Exiting.  vlan must be digits. Got {}.'.format(_x))
            exit(1)
        self._vlan = _x

    @property
    def total_cnt(self):
        try:
            return self.info['total_cnt']
        except:
            return -1

    @property
    def dyn_cnt(self):
        try:
            return self.info['dyn_cnt']
        except:
            return -1

    @property
    def otv_cnt(self):
        try:
            return self.info['otv_cnt']
        except:
            return -1

    @property
    def rvtep_static_cnt(self):
        try:
            return self.info['rvtep_static_cnt']
        except:
            return -1

    @property
    def static_cnt(self):
        try:
            return self.info['static_cnt']
        except:
            return -1

    @property
    def secure_cnt(self):
        try:
            return self.info['secure_cnt']
        except:
            return -1
