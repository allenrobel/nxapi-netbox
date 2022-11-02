#!/usr/bin/env python3
'''
Name: nxapi_bgp_neighbors_new.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes containing methods for retrieving bgp process information

Description:
   Creates three dicts:
      - self._global_dict contains global info about the bgp process
        accessed with instance.global_dict
      - self._vrf_dict, keyed on vrf_name, contains info about vrf_name
        accessed with instance.vrf_dict
      - self._af_dict, keyed on vrf_name, contains address-family info for vrf_name
        accessed with instance.af_dict
'''
our_version = 104

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiBgpProcess(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._af_dict = dict()
        self._vrf_dict = dict()
        self._global_dict = dict()

    def refresh(self):
        self.cli = 'show bgp process'
        self.show(self.cli)
        self.make_vrf_dict()
        self.make_af_dict()
        self.make_global_dict()

    def make_vrf_dict(self):
        self._vrf_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'vrf-name-out' not in _dict:
                continue
            vrf = _dict['vrf-name-out']
            self._vrf_dict[vrf] = _dict

    def make_af_dict(self):
        '''
        make dict, keyed on vrfname, with the following structure:
           af_dict[vrfname][af-id]["af-id"]
           af_dict[vrfname][af-id]["af-name"]
           af_dict[vrfname][af-id]["af-table-id"]
           af_dict[vrfname][af-id]["af-state"]
           af_dict[vrfname][af-id]["af-num-peers"]
           af_dict[vrfname][af-id]["af-num-active-peers"]
           af_dict[vrfname][af-id]["af-peer-routes"]
           af_dict[vrfname][af-id]["af-peer-paths"]
           af_dict[vrfname][af-id]["af-peer-networks"]
           af_dict[vrfname][af-id]["af-peer-aggregates"]
           af_dict[vrfname][af-id]["af-rr"]
           af_dict[vrfname][af-id]["default-information-enabled"]
           af_dict[vrfname][af-id]["nexthop-trigger-delay-critical"]
           af_dict[vrfname][af-id]["nexthop-trigger-delay-non-critical"]

            The following JSON is accessed (not all ROW_af dictionaries shown)

            "TABLE_af": {
                "ROW_af": [
                    {
                        "af-id": "0", 
                        "af-name": "IPv4 Unicast", 
                        "af-table-id": "1", 
                        "af-state": "UP", 
                        "af-num-peers": "2", 
                        "af-num-active-peers": "2", 
                        "af-peer-routes": "10", 
                        "af-peer-paths": "14", 
                        "af-peer-networks": "4", 
                        "af-peer-aggregates": "0", 
                        "af-rr": "false", 
                        "default-information-enabled": "false", 
                        "nexthop-trigger-delay-critical": "3000", 
                        "nexthop-trigger-delay-non-critical": "10000"
                    }, 
        '''
        self._af_dict = dict()
        for vrf in self._vrf_dict:
            self.af_dict[vrf] = dict()
            _list = self._get_table_row('af', self._vrf_dict[vrf])
            if _list == False:
                return
            for _dict in _list:
                if 'af-id' not in _dict:
                    self.log.warning('{} skipping. af-id key not in _dict {}'.format(self.hostname, _dict))
                    continue
                self.af_dict[vrf][_dict['af-id']] = _dict
                self.log.debug('got self.af_dict {}'.format(self.af_dict[vrf][_dict['af-id']]))

    def make_global_dict(self):
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        for _key in self.body[0]:
            if 'TABLE' in _key:
                continue
            self._global_dict[_key] = self.body[0][_key]
            self.log.debug('{} key {} value {}'.format(self.hostname, _key, self._global_dict[_key]))

    @property
    def af_dict(self):
        return self._af_dict

    @property
    def global_dict(self):
        return self._global_dict

    @property
    def vrf_dict(self):
        return self._vrf_dict
