#!/usr/bin/env python3
'''
Name: nxapi_vrf.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes for retrieving vrf information

Description:
   Uses the following JSON data:

    ts_101# show vrf  | json-pretty 
    {
        "TABLE_vrf": {
            "ROW_vrf": [
                {
                    "vrf_name": "TENANT_1", 
                    "vrf_id": "3", 
                    "vrf_state": "Up", 
                    "vrf_reason": "--"
                }, 
                {
                    "vrf_name": "default", 
                    "vrf_id": "1", 
                    "vrf_state": "Up", 
                    "vrf_reason": "--"
                }, 
                {
                    "vrf_name": "management", 
                    "vrf_id": "2", 
                    "vrf_state": "Up", 
                    "vrf_reason": "--"
                }
            ]
        }
    }

Synopsis:

from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_vrf import NxapiVrf

def print_header():
    print("{:<15} {:<15} {:<6} {:<9} {:<30}".format(
        'hostname', 'vrf_name', 'vrf_id', 'vrf_state', 'vrf_reason'))

def print_info(vrf):
    for vrf_name in sorted(vrf.info):
        print("{:<15} {:<15} {:<6} {:<9} {:<30}".format(
            vrf.hostname,
            vrf.info[vrf_name]['vrf_name'],
            vrf.info[vrf_name]['vrf_id'],
            vrf.info[vrf_name]['vrf_state'],
            vrf.info[vrf_name]['vrf_reason']))

log = get_logger('my_script', 'INFO', 'DEBUG')
vrf = NxapiVrf('admin','mypassword','192.168.1.1',log)
# cookies from DUT will be processed by default. pass argparse instance
# to nxapi_init to disable various cookie-related functions
# see repos/dssperf/lib3/cargs_sid.py for specific arguments
vrf.nxapi_init()
vrf.refresh()
print_header()
print_info(vrf)
'''
our_version = 104

# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiVrf(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info = dict()

    def refresh(self):
        self.cli = 'show vrf'
        self.show()
        self.make_info_dict()

    def make_info_dict(self):
        self._info = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        try:
            _dicts = self._convert_to_list(self.body[0]['TABLE_vrf']['ROW_vrf'])
        except:
            self.log.warning('{} returning empty self._addrf_dict due to key [TABLE_vrf][ROW_vrf] not found in self.body[0] {}'.format(self.hostname, self._vrf_dict))
            return

        _vrfs = self._convert_to_list(_dicts)
        for _vrf_dict in _vrfs:
            if 'vrf_name' not in _vrf_dict:
                self.log.debug('{} skipping. vrf_name key not in _vrf_dict {}'.format(self.hostname, _vrf_dict))
                continue
            self._info[_vrf_dict['vrf_name']] = dict()
            for _key in _vrf_dict:
                self.log.debug('got _key {} from _vrf_dict'.format(_key))
                if 'TABLE' not in _key:
                    self._info[_vrf_dict['vrf_name']][_key] = _vrf_dict[_key]
                else:
                    self.log.debug('skipping unexpected TABLE {} in _vrf_dict {}'.format(_key, _vrf_dict))

    @property
    def info(self):
        return self._info
