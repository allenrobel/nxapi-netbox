#!/usr/bin/env python3
'''
Name: nxapi_boot.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes for retrieving bootvar information from a NXOS switch via NXAPI

Description:

Synopsis:

import argparse
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_boot import NxapiBoot

ip = '192.168.1.1'
username = 'admin'
password = 'mypassword'
log = get_logger('my_script', 'INFO', 'DEBUG')
nx = NxapiBoot(username, password, ip, log)
nx.nxapi_init(cfg)
nx.refresh()
# sup #1
nx.sup_instance = 1 # get info for first sup instance
print('sup {} current_image {}'.format(nx.sup_instance, nx.current_image))
print('sup {} poap_status   {}'.format(nx.sup_instance, nx.poap_status))

nx.sup_instance = 2 # get info for 2nd sup instance
# if sup_instance does not exist, False is returned for all values
print('sup {} current_image {}'.format(nx.sup_instance, nx.current_image))
print('sup {} poap_status   {}'.format(nx.sup_instance, nx.poap_status))

# > 2 instances are supported, but no NXOS switches currently offer > 2 supervisor modules (AFAIK)

# if sup_instance does not exist, False is returned for all values
nx.sup_instance = 8 # get info for the 8th sup instance
print('sup {} current_image {}'.format(nx.sup_instance, nx.current_image))
print('sup {} poap_status   {}'.format(nx.sup_instance, nx.poap_status))
'''
our_version = 104

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiBoot(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.cli = 'show boot'
        self.info = dict()
        self.info[1] = dict()
        self.info[2] = dict()
        self.info[1]['current'] = dict()
        self.info[1]['startup'] = dict()
        self.info[2]['current'] = dict()
        self.info[2]['startup'] = dict()
        # set with @sup_instance
        # determines which instance will be returned from the various read_only @properties
        self._sup_instance = 1

    def refresh(self):
        self.show(self.cli)
        self.make_info_dict()

    def convert_to_list(self, value):
        '''
        The returned list will always have at least two values.
        For single sup, the 2nd value is set to False
        '''
        if type(value) == type(list()):
            return value
        return [value, False]

    def make_info_dict(self):
        '''
        creates self.info, a three-level dict() with the following structure:
            self.info[<sup instance>]['current']['image']
            self.info[<sup instance>]['current']['poap_status']

            self.info[<sup instance>]['startup']['image']
            self.info[<sup instance>]['startup']['poap_status']

        The number of <sup instance> is determined by whether or not 'current_sup_module', 'start_sup_module' are lists.
        If not lists, then there is a single sup.  In this case, we populate two <sup instance> (with values for instance 2 being set to False)
        If lists, then there are multiple sups.  In this case, we populate as many <sup instance> as there are sups

        The following JSON is referenced (from 'show boot' CLI)

        Single sup:

        switch# sh boot | json-pretty 
        {
            "TABLE_Current_Bootvar": {
                "ROW_Current_Bootvar": {
                    "current_sup_module": "sup-1", 
                    "current_image": "bootflash:/nxos.9.2.3.bin", 
                    "current_poap_status": "Disabled"
                }
            }, 
            "TABLE_Startup_Bootvar": {
                "ROW_Startup_Bootvar": {
                    "start_sup_module": "sup-1", 
                    "start_image": "bootflash:/nxos.9.2.3.bin", 
                    "start_poap_status": "Disabled"
                }
            }
        }
        switch# 


        Dual sup:

        switch# sh boot | json-pretty 
        {
            "TABLE_Current_Bootvar": {
                "ROW_Current_Bootvar": {
                    "current_sup_module": [
                        "sup-1", 
                        "sup-2"
                    ], 
                    "current_image": [
                        "bootflash:/nxos.9.2.3.bin", 
                        "bootflash:/nxos.9.2.3.bin"
                    ], 
                    "current_poap_status": "Disabled"
                }
            }, 
            "TABLE_Startup_Bootvar": {
                "ROW_Startup_Bootvar": {
                    "start_sup_module": [
                        "sup-1", 
                        "sup-2"
                    ], 
                    "start_image": [
                        "bootflash:/nxos.9.2.3.bin", 
                        "bootflash:/nxos.9.2.3.bin"
                    ], 
                    "start_poap_status": "Disabled"
                }
            }
        }
        switch# 

        '''

        self.info = dict()
        # by default, we populate two sup instances.
        # if single sup, then values for instance 2 are set to False
        # if dual sup, all values are populated from the json
        # if > 2 sups, add additional instances
        self.info[1] = dict()
        self.info[2] = dict()
        self.info[1]['current'] = dict()
        self.info[1]['startup'] = dict()
        self.info[2]['current'] = dict()
        self.info[2]['startup'] = dict()
        self.info[1]['current']['image'] = False
        self.info[1]['startup']['poap_status'] = False
        self.info[2]['current']['image'] = False
        self.info[2]['startup']['poap_status'] = False

        if not self._verify_body_length():
            return
        _list = self._get_table_row('Current_Bootvar', self.body[0])
        if _list == False:
            return
        _dict_current = _list[0]

        _list = self._get_table_row('Startup_Bootvar', self.body[0])
        if _list == False:
            return
        _dict_startup = _list[0]

        try:
            _sup = _dict_current['current_sup_module']
        except:
            self.log.error('{} Exiting. current_sup_module not found in _dict_current {}'.format(_dict_current))
            exit(1)

        if type(_sup) == type(list()):
            self.num_current_sup = len(_sup)
        else:
            self.num_current_sup = 1

        if self.num_current_sup > 1:
            for _sup_instance in range(1, self.num_current_sup+1):
                self.info[_sup_instance] = dict()
                self.info[_sup_instance]['current'] = dict()
                self.info[_sup_instance]['startup'] = dict()
        else:
            # single-sup, so create two instances since we want to ensure at least two entries always
            for _sup_instance in [1,2]:
                self.info[_sup_instance] = dict()
                self.info[_sup_instance]['current'] = dict()
                self.info[_sup_instance]['startup'] = dict()

        # current
        _image_list = list()
        try:
            _image_list = self.convert_to_list(_dict_current['current_image'])
        except:
            self.log.debug('{} unable to convert current_image to list. Setting to False')
            _image_list = [False, False]

        for _sup_instance in self.info:
            try:
                self.info[_sup_instance]['current']['image'] = _image_list[_sup_instance - 1]
            except:
                self.log.debug('{} current_image not found. Setting to False'.format(self.hostname))
                self.info[_sup_instance]['current']['image'] = False

            # poap_status is never a list (at least as of NXOS 9.2(3))
            try:
                self.info[_sup_instance]['current']['poap_status'] = _dict_current['current_poap_status']
            except:
                self.log.debug('{} current_poap_status not found in _dict_current {}. Setting to False'.format(self.hostname, _dict_current))
                self.info[_sup_instance]['current']['poap_status'] = False

        # startup
        _image_list = list()
        try:
            _image_list = self.convert_to_list(_dict_startup['start_image'])
        except:
            self.log.debug('{} unable to convert start_image to list. Setting to False')
            _image_list = [False, False]

        for _sup_instance in self.info:
            try:
                self.info[_sup_instance]['startup']['image'] = _image_list[_sup_instance - 1]
            except:
                self.log.debug('{} start_image not found. Setting to False'.format(self.hostname))
                self.info[_sup_instance]['startup']['image'] = False

            # poap_status is never a list (at least as of NXOS 9.2(3))
            try:
                #self.info[_sup_instance]['startup']['poap_status'] = _dict_startup['TABLE_Startup_Bootvar']['ROW_Startup_Bootvar']['start_poap_status']
                self.info[_sup_instance]['startup']['poap_status'] = _dict_startup['start_poap_status']
            except:
                self.log.debug('{} start_poap_status not found. Setting to False'.format(self.hostname))
                self.info[_sup_instance]['startup']['poap_status'] = False


    @property
    def sup_instance(self):
        return self._sup_instance
    @sup_instance.setter
    def sup_instance(self, x):
        try:
            self._sup_instance = int(str(x))
        except:
            self.log.error('Exiting. Expected an integer for sup_instance. Got {}'.format(x))
            exit(1)

    @property
    def current_image(self):
        try:
            return self.info[self.sup_instance]['current']['image']
        except:
            return False

    @property
    def current_poap_status(self):
        try:
            return self.info[self.sup_instance]['current']['poap_status']
        except:
            return False


    @property
    def startup_image(self):
        try:
            return self.info[self.sup_instance]['startup']['image']
        except:
            return False

    @property
    def startup_poap_status(self):
        try:
            return self.info[self.sup_instance]['startup']['poap_status']
        except:
            return False

