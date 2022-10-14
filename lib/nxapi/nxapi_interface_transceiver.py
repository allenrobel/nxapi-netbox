#!/usr/bin/env python3
our_version = 101
'''
Name: nxapi_interface_transceiver.py
Author: Allen Robel (arobel@cisco.com)
Description:

Classes containing methods for retrieving interface transceiver information via NXAPI

Revision history: use git log

Example script: See dssperf/python/lib3/unit_test_nxapi_interface_transceiver.py

Example of json data processed by this class.

switch# show interface transceiver | json-pretty 
{
    "TABLE_interface": {
        "ROW_interface": [
            {
                "interface": "Ethernet1/1", 
                "sfp": "present", 
                "type": "QSFP-100G-AOC1M", 
                "name": "CISCO-FINISAR", 
                "partnum": "FCBN425QE1C01-C1", 
                "rev": "D", 
                "serialnum": "FIW203103ZC-A", 
                "nom_bitrate": "25500", 
                "ciscoid": "17", 
                "ciscoid_1": "220", 
                "cisco_part_number": "10-3172-01", 
                "cisco_product_id": "QSFP-100G-AOC1M", 
                "cisco_vendor_id": "V01"
            }, 
            {
                "interface": "Ethernet1/2", 
                "sfp": "present", 
                "type": "QSFP-100G-AOC1M", 
                "name": "CISCO-FINISAR", 
                "partnum": "FCBN425QE1C01-C1", 
                "rev": "D", 
                "serialnum": "FIW202005PK-A", 
                "nom_bitrate": "25500", 
                "ciscoid": "17", 
                "ciscoid_1": "220", 
                "cisco_part_number": "10-3172-01", 
                "cisco_product_id": "QSFP-100G-AOC1M", 
                "cisco_vendor_id": "V01"
            }, 
            etc...
        ]
    }
}
'''

from nxapi.nxapi_base import NxapiBase
from copy import deepcopy

class NxapiInterfaceTransceiver(NxapiBase):
    '''
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self.lib_name = 'NxapiInterfaceTransceiver'
        self.log_prefix = '{}_v{}'.format(self.lib_name, self.lib_version)
        self.properties = dict()
        self.properties['interface'] = None
        self.properties['info'] = dict()
        self.properties['interfaces'] = list()
        self.refreshed = False
        self.default_dict = dict()
        self.default_dict['sfp'] = 'na'
        self.default_dict['type'] = 'na'
        self.default_dict['name'] = 'na'
        self.default_dict['partnum'] = 'na'
        self.default_dict['rev'] = 'na'
        self.default_dict['serialnum'] = 'na'
        self.default_dict['nom_bitrate'] = 999999999999
        self.default_dict['ciscoid'] = 'na'
        self.default_dict['ciscoid_1'] = 'na'
        self.default_dict['cisco_part_number'] = 'na'
        self.default_dict['cisco_product_id'] = 'na'
        self.default_dict['cisco_vendor_id'] = 'na'

    def refresh(self):
        self.refreshed = False
        if self.interface == None:
            self.cli = 'show interface transceiver'
        else:
            self.cli = 'show interface {} transceiver'.format(self.interface)
        self.log.debug('{} {} using cli {}'.format(self.log_prefix, self.hostname, self.cli))
        self.show(self.cli)
        self.make_info_dict()

        for k in self.properties['info']:
            if 'interface' not in self.properties['info'][k]:
                return False
        self.refreshed = True

    def make_info_dict(self):
        self.properties['info'] = dict()
        self.properties['interfaces'] = list()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        L = self._get_table_row('interface', self.body[0])
        if L == False:
            return
        for D in L:
            try:
                interface = D['interface']
            except:
                self.log.debug('{} [interface] key not in dict {}'.format(self.hostname, D))
                return
            try:
                sfp = D['sfp']
            except:
                self.log.debug('{} [sfp] key not in dict {}'.format(self.hostname, D))
                return

            if sfp == 'present':
                self.properties['info'][interface] = D
                self.properties['interfaces'].append(interface)
            else:
                dd = deepcopy(self.default_dict)
                dd['interface'] = interface
                self.properties['info'][interface] = deepcopy(dd)

    def verify_params(self, p):
        if self.refreshed == False:
            self.log.error('exiting. call instance.refresh() before calling instance.{}'.format(p))
            exit(1)
        if self.interface == None:
            self.log.error('exiting. set instance.interface before calling instance.{}'.format(p))
            exit(1)

    @property
    def interface(self):
        return self.properties['interface']
    @interface.setter
    def interface(self, x):
        self.properties['interface'] = x

    @property
    def interfaces(self):
        '''
        returns a list() of interfaces on the switch that contain transceivers.
        '''
        if self.refreshed == False:
            self.log.error('exiting. call instance.refresh() before calling instance.interfaces')
            exit(1)
        return self.properties['interfaces']

    @property
    def info(self):
        '''
        return the main dictionary created by this library
        '''
        try:
            return self.properties['info']
        except:
            return dict()

    @property
    def ciscoid(self):
        self.verify_params('ciscoid')
        try:
            return str(self.properties['info'][self.interface]['ciscoid'])
        except:
            return 'na'
    @property
    def ciscoid_1(self):
        self.verify_params('ciscoid_1')
        try:
            return str(self.properties['info'][self.interface]['ciscoid_1'])
        except:
            return 'na'
    @property
    def cisco_part_number(self):
        self.verify_params('cisco_part_number')
        try:
            return self.properties['info'][self.interface]['cisco_part_number']
        except:
            return 'na'
    @property
    def cisco_product_id(self):
        self.verify_params('cisco_product_id')
        try:
            return self.properties['info'][self.interface]['cisco_product_id']
        except:
            return 'na'
    @property
    def cisco_vendor_id(self):
        self.verify_params('cisco_vendor_id')
        try:
            return self.properties['info'][self.interface]['cisco_vendor_id']
        except:
            return 'na'
    @property
    def name(self):
        self.verify_params('name')
        try:
            return self.properties['info'][self.interface]['name']
        except:
            return 'na'
    @property
    def nom_bitrate(self):
        self.verify_params('nom_bitrate')
        try:
            return int(self.properties['info'][self.interface]['nom_bitrate'])
        except:
            return 'na'
    @property
    def partnum(self):
        self.verify_params('partnum')
        try:
            return self.properties['info'][self.interface]['partnum']
        except:
            return 'na'
    @property
    def rev(self):
        self.verify_params('rev')
        try:
            return self.properties['info'][self.interface]['rev']
        except:
            return 'na'
    @property
    def sfp(self):
        self.verify_params('sfp')
        try:
            return self.properties['info'][self.interface]['sfp']
        except:
            return 'na'
    @property
    def sfp_type(self):
        self.verify_params('sfp_type')
        try:
            return self.properties['info'][self.interface]['type']
        except:
            return 'na'
    @property
    def serialnum(self):
        self.verify_params('serialnum')
        try:
            return self.properties['info'][self.interface]['serialnum']
        except:
            return 'na'
