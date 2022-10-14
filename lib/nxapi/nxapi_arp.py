#!/usr/bin/env python3
'''
Name: nxapi_arp.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving arp information 

NxapiArpSummary() corresponds to the output provided by the following cli:

show ip arp summary

switch# sh ip arp summary | json-pretty 
{
    "TABLE_vrf": {
        "ROW_vrf": {
            "vrf-name-out": "default", 
            "cnt-resolved": "6", 
            "cnt-incomplete": "0", 
            "cnt-thrtld-incomplete": "0", 
            "cnt-unknown": "0", 
            "cnt-total": "6"
        }
    }
}
'''
our_version = 106

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiArpSummary(NxapiBase):
    '''
    Methods for parsing the JSON below.

    switch# sh ip arp summary | json-pretty 
    {
        "TABLE_vrf": {
            "ROW_vrf": {
                "vrf-name-out": "default", 
                "cnt-resolved": "6", 
                "cnt-incomplete": "0", 
                "cnt-thrtld-incomplete": "0", 
                "cnt-unknown": "0", 
                "cnt-total": "6"
            }
        }
    }


    Creates a dictionary, self.info, with the following structure:

    self.info['resolved'] = int()
    self.info['incomplete'] = int()
    self.info['throttled'] = int()
    self.info['unknown'] = int()
    self.info['total'] = int()

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch
    self.vrf - the vrf in which arps were queried (defaults to vrf 'default')

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self._vrf = 'default'

    def _get_vrf_dict(self):
        '''
        sets self._vrf_dict

        self._vrf_dict will contain the information associated with self.vrf
        if expected keys are not present, self._vrf_dict will be empty
        {
            "TABLE_vrf": {
                "ROW_vrf": {   <<<<<<<<<<<<<<<<<<<
                    "vrf-name-out": "default", 
                    "cnt-resolved": "6", 
                    "cnt-incomplete": "0", 
                    "cnt-thrtld-incomplete": "0", 
                    "cnt-unknown": "0", 
                    "cnt-total": "6"
                }
            }
        }
        '''
        self._vrf_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'vrf-name-out' not in _dict:
                continue
            if _dict['vrf-name-out'] != self.vrf:
                continue
            self._vrf_dict = _dict

    def make_info_dict(self):
        '''
        from self.body populate self.info dict(),
        dict() structure is:
            self.info['resolved'] = int()
            self.info['incomplete'] = int()
            self.info['throttled'] = int()
            self.info['unknown'] = int()
            self.info['total'] = int()
        '''
        self.info = dict()
        self._get_vrf_dict()

        if len(self._vrf_dict) == 0:
            self.log.debug('{} Returning empty self.info dict() due to unable to find appropriate path in {}'.format(
                self.hostname,
                self.body))
            self.info = dict()
            return
        _expected_keys = ['cnt-resolved', 'cnt-incomplete', 'cnt-thrtld-incomplete', 'cnt-unknown', 'cnt-total']
        for key in _expected_keys:
            if key not in self._vrf_dict:
                self.log.debug('{} Returning empty self.info dict() due to key {} not found in self._vrf_dict {}'.format(
                    self.hostname,
                    self._vrf_dict))
                return
        self.info['resolved'] = self._vrf_dict['cnt-resolved']
        self.info['incomplete'] = self._vrf_dict['cnt-incomplete']
        self.info['throttled'] = self._vrf_dict['cnt-thrtld-incomplete']
        self.info['unknown'] = self._vrf_dict['cnt-unknown']
        self.info['total'] = self._vrf_dict['cnt-total']

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for key in self.info:
            self.log.info('{} self.info[{}] = {}'.format(self.hostname, key, self.info[key]))

    def refresh(self):
        self.cli = 'show ip arp summary vrf {}'.format(self.vrf)
        self.show(self.cli)
        self.make_info_dict()

    @property
    def resolved(self):
        try:
            return self.info['resolved']
        except:
            return -1

    @property
    def incomplete(self):
        try:
            return self.info['incomplete']
        except:
            return -1

    @property
    def throttled(self):
        try:
            return self.info['throttled']
        except:
            return -1

    @property
    def unknown(self):
        try:
            return self.info['unknown']
        except:
            return -1

    @property
    def total(self):
        try:
            return self.info['total']
        except:
            return -1

