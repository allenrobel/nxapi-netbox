#!/usr/bin/env python3
'''
Name: nxapi_locator_led_status.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes containing methods for retrieving locator-led status


Synopsis:

from nxapi_netbox.nxapi.nxapi_locator_led import NxapiLocatorLedStatus
from nxapi_netbox.general.log import get_logger

log = get_logger('my_script_name', 'INFO', 'DEBUG')
nx = NxapiLocatorLedStatus('myusername','mypassword','myip', log)
nx.refresh()
print('chassis status {}'.format(nx.chassis))
nx.module = 1
nx.fan = 1
print('module {} status {}'.format(nx.module, nx.module_status))
print('fan {} status {}'.format(nx.fan, nx.fan_status))


Description:

   Uses the following JSON data:

    switch# show locator-led status | json-pretty 
    {
        "TABLE_loc_led_stat": {
            "ROW_loc_led_stat": [
                {
                    "component": "Chassis", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 1", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 2", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 22", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 24", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 26", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 27", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 29", 
                    "status": "OFF"
                }, 
                {
                    "component": "Module 30", 
                    "status": "OFF"
                }, 
                {
                    "component": "FAN Module 1", 
                    "status": "OFF"
                }, 
                {
                    "component": "FAN Module 2", 
                    "status": "OFF"
                }, 
                {
                    "component": "FAN Module 3", 
                    "status": "OFF"
                }
            ]
        }
    }
    switch# 

'''
our_version = 104

# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiLocatorLedStatus(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info = dict()
        self._refreshed = False
        self._is_module_set = False
        self._is_fan_set = False
        self._module = None
        self._fan = None
        self.map_keys = dict()
        self.map_keys['Chassis'] = 'chassis'
        for module in range(1,33):
            self.map_keys['Module {}'.format(module)] = 'module_{}'.format(module)
        for fan in range(1,9):
            self.map_keys['FAN Module {}'.format(fan)] = 'fan_{}'.format(fan)

    def refresh(self):
        self.cli = 'show locator-led status'
        self.show(self.cli)
        self.make_info_dict()

    def _populate_info_dict(self):
        self.log.debug('GOT self.body {}'.format(self.body))
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        _op = self.body[0]
        if 'TABLE_loc_led_stat' not in _op:
            self.log.debug('{} early return: no TABLE_loc_led_stat'.format(self.hostname))
            return
        if 'ROW_loc_led_stat' not in _op['TABLE_loc_led_stat']:
            self.log.debug('{} early return: no ROW_loc_led_stat'.format(self.hostname))
            return
        _dicts = self._convert_to_list(_op['TABLE_loc_led_stat']['ROW_loc_led_stat'])
        for _dict in _dicts:
            if 'component' not in _dict:
                self.log.debug('{} skipping. [component] key not in _dict {}'.format(self.hostname, _dict))
                continue
            if 'status' not in _dict:
                self.log.debug('{} skipping. [status] key not in _dict {}'.format(self.hostname, _dict))
                continue
            try:
                component = _dict['component']
                converted_component = self.map_keys[component]
                status = _dict['status']
                self._info[converted_component] = status
            except:
                self.log.debug('skipping. Cannot process _dict {}'.format(_dict))
                continue

    def make_info_dict(self):
        self._info = dict()
        self._populate_info_dict()
        self._refreshed = True

    @property
    def is_module_set(self):
        return self._is_module_set
    @property
    def is_fan_set(self):
        return self._is_fan_set

    def check_refreshed(self):
        if self.refreshed == False:
            self.log.error('Exiting. Please call instance.refresh() first.')
            exit(1)
    def check_is_module_set(self):
        if self.is_module_set == False:
            self.log.error('Exiting. Please set instance.module first. E.g. instance.module = 2')
            exit(1)
    def check_is_fan_set(self):
        if self.is_fan_set == False:
            self.log.error('Exiting. Please set instance.fan first. E.g. instance.fan = 1')
            exit(1)

    @property
    def refreshed(self):
        return self._refreshed

    @property
    def chassis(self):
        try:
            return self.info['chassis']
        except:
            return False

    @property
    def info(self):
        '''
        returns the raw info dict()
        '''
        self.check_refreshed()
        return self._info

    @property
    def module(self):
        return self._module
    @module.setter
    def module(self, _x):
        try:
            self._module = int(str(_x))
        except:
            self.log.error('Exiting. Expected int() for module.  Got {}'.format(_x))
            exit(1)
        self._is_module_set = True

    @property
    def fan(self):
        return self._fan
    @fan.setter
    def fan(self, _x):
        try:
            self._fan = int(str(_x))
        except:
            self.log.error('Exiting. Expected int() for fan.  Got {}'.format(_x))
            exit(1)
        self._is_fan_set = True


    @property
    def module_status(self):
        self.check_refreshed()
        self.check_is_module_set()
        try:
            return self._info['module_{}'.format(self.module)]
        except:
            return -1

    @property
    def fan_status(self):
        self.check_refreshed()
        self.check_is_fan_set()
        try:
            return self._info['fan_{}'.format(self.fan)]
        except:
            return -1
