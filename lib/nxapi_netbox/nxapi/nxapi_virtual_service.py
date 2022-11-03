#!/usr/bin/env python3
'''
Name: nxapi_virtual_service.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving virtual service info from a NXOS switch via NXAPI

Example usage:

from nxapi_netbox.nxapi.nxapi_virtual_service import NxapiVirtualServiceList
from nxapi_netbox.general import get_logger
log = get_logger('my_script_name', 'INFO', 'DEBUG') # INFO for screen logging, DEBUG for file logging
nx = NxapiVirtualServiceList('myusername','mypassword','myip', log)
nx.nxapi_init()
nx.refresh()
for service in nx.services:
    nx.service = service
    print('{:<15} {:<20} {:<15} {:<15}'.format(ip, nx.hostname, nx.service, nx.status))

'''
our_version = 102

# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiVirtualServiceList(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.services = list() # list of services present on device
        self._service = None
        self.refreshed = False
        self.cli = 'show virtual-service list'
    def refresh(self):
        self.services = list()
        self.show()
        self.make_info_dict()
        self.refreshed = True
    def make_info_dict(self):
        '''
        creates self.info, a single-level dict() with the following structure:
            self.info['host_id']

        The following JSON is referenced

            tor_311# show virtual-service list | json-pretty
            {
                "TABLE_list": {
                    "ROW_list": {
                        "name": "guestshell+", 
                        "status": "Activated", 
                        "package_name": "guestshell.ova"
                    }
                }
            }
            tor_311# 

        '''
        self.info = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return

        try:
            _dicts = self._convert_to_list(self.body[0]['TABLE_list']['ROW_list'])
        except:
            self.log.warning('{} Setting empty _dicts due to key [TABLE_list][ROW_list] not found in self.body[0] {}'.format(self.hostname, self.body[0]))
            return

        for _service in _dicts:
            if 'name' not in _service:
                self.log.debug('{} service {} contains no [name] key.  Skipping.'.format(self.hostname))
                continue
            self.services.append(_service['name'])
            self.info[_service['name']] = dict()
            self.info[_service['name']]['name'] = _service['name']
            self.info[_service['name']]['status'] = _service['status']
            self.info[_service['name']]['package_name'] = _service['package_name']

    @property
    def name(self):
        try:
            return self.info[self.service]['name']
        except:
            return -1

    @property
    def status(self):
        try:
            return self.info[self.service]['status']
        except:
            return -1

    @property
    def package_name(self):
        try:
            return self.info[self.service]['package_name']
        except:
            return -1

    @property
    def service(self):
        return self._service
    @service.setter
    def service(self, _x):
        self._service = _x
