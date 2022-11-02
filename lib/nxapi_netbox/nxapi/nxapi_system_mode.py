#!/usr/bin/env python3
'''
Name: nxapi_system_mode.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving system mode state via NXAPI

NxapiSystemMode() corresponds to the output provided by the following cli:

show system mode | json-pretty
'''
our_version = 101

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase
from nxapi_netbox.general.verify_types import VerifyTypes

class NxapiSystemMode(NxapiBase):
    '''
    Methods for retrieving the output of the following CLI via NXAPI:

    show system mode

    The following states are possible

    {
        "system_mode": "Normal", 
        "timer_state": "switch to maintenance mode in progress"
    }

    {
        "system_mode": "Normal"
        "timer_state": "na"      << added by this class if timer_state key is missing
    }

    {
    "system_mode": "Maintenance"
    "timer_state": "switch to normal mode in progress"
    }

    {
    "system_mode": "Maintenance"
    "timer_state": "not running"
    }

    Resulting dictionary structure can be retrieved with three properties:

    mode = sm.system_mode
    timer = sm.timer_state

    system_mode_dict = sm.info

    self.hostname -  will equal the value of the hostname configuration on the target switch

    hostname = sm.hostname

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info_dict = dict()
        self.verify = VerifyTypes(self.log)

    def make_info_dict(self):
        '''
        from self.body populate self._info_dict dict(),
        dict() structure is identical to returned JSON except for package_list/
        '''
        self._info_dict = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        try:
            _dict = self.body[0]
        except:
            self.log.debug('{} early return: unable to find dict() in self.body[0] {}'.format(self.hostname, self.body[0]))
            return

        for key in _dict:
            self._info_dict[key] = _dict[key]

        if 'timer_state' not in self._info_dict:
            self._info_dict['timer_state'] = 'na'

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for key in self._info_dict:
            self.log.info('{} self._info_dict[{}] = {}'.format(self.hostname, key, self._info_dict[key]))

    def refresh(self):
        self.cli = 'show system mode'
        self.show(self.cli)
        self.make_info_dict()
 
    @property
    def system_mode(self):
        try:
            return self._info_dict['system_mode']
        except:
            return 'na'

    @property
    def timer_state(self):
        try:
            return self._info_dict['timer_state']
        except:
            return 'na'

    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info_dict
        except:
            return dict()
