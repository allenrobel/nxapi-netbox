#!/usr/bin/env python3
'''
Name: nxapi_config.py
Author: Allen Robel (arobel@cisco.com)
Description: NXAPI: Classes containing methods for configuring an NXOS switch

Synopsis:

from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_config import NxapiConfig

script_name = 'my_script'
log = get_logger(script_name, 'INFO', 'DEBUG')

c = NxapiConfig('my_username','my_password','my_ip', log)
c.config_file = '/tmp/myconfig.cfg'
c.commit_file()

Or:

c = NxapiConfig('myusername','mypassword','myip', log)
cfg = list()
cfg.append('interface Eth1/1')
cfg.append(' ip address 1.1.1.1/24')
c.config_list = cfg
c.commit_list()
'''
our_version = 111

from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiConfig(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
    def commit_file(self):
        '''
        configure dut from a file containing config commands
        expects self.config_file to contain config commands
        '''
        if self.config_file == None:
            self.log.error('Exiting. self.config_file must be set first')
            exit(1)
        self.configure_from_file()
        if self.result_code != self.RC_200_SUCCESS:
            self.log.error("NxapiConfig.commit_file: {} {} Unable to commit file {} due to result_code {}".format(
                self.mgmt_ip,
                self.hostname,
                self.config_file,
                self.result_code))
            return False
        return True
    def commit_list(self):
        '''
        configure dut from a list of config commands
        expects self.config_list to contain config commands
        '''
        self.configure_from_list()
        if self.result_code != self.RC_200_SUCCESS:
            self.log.error("NxapiConfig.commit_list: {} {} Unable to commit list due to result_code {}".format(
                self.mgmt_ip,
                self.hostname,
                self.result_code))
            return False
        return True
