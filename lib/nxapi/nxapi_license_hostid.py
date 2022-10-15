#!/usr/bin/env python3
'''
Name: nxapi_license_hostid.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes containing methods for retrieving license host_id from a NXOS switch via NXAPI

Description:

Synopsis:

from nxapi.nxapi_license_hostid import NxapiLicenseHostid
from general.log import get_logger

def print_dict(d, hostname):
    width = get_max_width(d)
    for peer in d:
        for key in sorted(d[peer]):
            value = d[peer][key]
            if type(value) != type(dict()):
                print("{:<15} {:<15} {:<{width}} {}".format(hostname, peer, key, value, width=width))
                continue
            for k in value:
                print("{:<15} {:<15} {:<{width}} {}".format(hostname, peer, k, value[k], width=width))
        print()

log = get_logger('my_script_name', 'INFO', 'DEBUG')
d = NxapiLicenseHostid('myusername','mypassword','myip', log)
# note, if argparse instance is not provided, cookies will be used by default
d.nxapi_init()
d.refresh()
print_dict(d.info, d.hostname)
# access via @property (recommended)
print('host-id {}'.format(d.host_id))
# direct dictionary access
print('host-id {}'.format(d.info['host_id']))
'''
our_version = 102

# standard libraries
import re
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiLicenseHostid(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.info['host_id'] = None
        self.refreshed = False
        self.cli = 'show license host-id'
    def refresh(self):
        self.show(self.cli)
        self.make_info_dict()
    def make_info_dict(self):
        '''
        creates self.info, a single-level dict() with the following structure:
            self.info['host_id']

        The following JSON is referenced

            switch# show license host-id | json-pretty
            {
                "host_id": "VDH=FDO2321135M"
            }
            switch# 

        '''
        self.info = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        if 'host_id' not in self.body[0]:
            self.log.debug('{} early return: no host_id'.format(self.hostname))
            return
        self.info['host_id_raw'] = self.body[0]['host_id']
        self.info['host_id'] = re.split('=', self.body[0]['host_id'])[1]

    @property
    def host_id(self):
        '''
        return the hostid without the VDH= portion e.g. FDO2321135M
        '''
        try:
            return self.info['host_id']
        except:
            return -1

    @property
    def host_id_raw(self):
        '''
        return the raw hostid we.g. VDH=FDO2321135M
        '''
        try:
            return self.info['host_id_raw']
        except:
            return -1
