#!/usr/bin/env python3
'''
Name: nxapi_interface_queuing_tabular.py
Author: Allen Robel (arobel@cisco.com)
Description: Class containing methods for retrieving interface queuing counters

Synopsis:
'''
our_version = 102

# standard libraries
from copy import deepcopy
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiInterfaceQueuingTabular(NxapiBase):
    '''
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)

        self._interface = None
        self.info = dict()

        self.properties = dict()
        self.properties['interface'] = None
        self.properties['qos_group'] = None
        self.properties['counter'] = None

        self.valid_counter_name = set()
        self.valid_counter_name.add('uc-tx-pkts')
        self.valid_counter_name.add('uc-drop-pkts')
        self.valid_counter_name.add('uc-ecn-mark-pkts')
        self.valid_counter_name.add('flood-tx-pkts')
        self.valid_counter_name.add('flood-drop-pkts')
        self.valid_counter_name.add('mc-tx-pkts')
        self.valid_counter_name.add('mc-drop-pkts')
        self.valid_counter_name.add('pfc-tx-pkts')
        self.valid_counter_name.add('pfc-rx-pkts')
        self.valid_counter_name.add('uc-tx-pkt-rate')
        self.valid_counter_name.add('uc-tx-byte-rate')
        self.valid_counter_name.add('uc-drop-pkt-rate')
        self.valid_counter_name.add('uc-drop-byte-rate')

        self.counter_names = sorted(self.valid_counter_name)

        self.qos_groups = [0,1,2,3,4,5,6,7,'cpu','span']
        self.valid_qos_group = set()
        for x in self.qos_groups:
            self.valid_qos_group.add(x)

    def _get_queuing_interface_dict_from_module_dict(self):
        '''
        Populates a dict(), which will be empty if expected keys are not present.
        Else, will contain everything in TABLE_queuing_interface and below.
        '''
        self._queuing_interface_dict = dict()
        _list = self._get_table_row('queuing_interface', self._module_dict)
        if _list == False:
            return
        self._queuing_interface_dict = _list[0]

    def _get_queuing_counter_dict_from_queuing_interface_dict(self):
        '''
        Populates a dict(), which will be empty if expected keys are not present.
        Else, will contain everything in TABLE_queuing_interface and below.
        '''
        self._queuing_counter_dict = dict()
        _list = self._get_table_row('queuing_counter', self._queuing_interface_dict)
        if _list == False:
            return
        for d in _list:
            if 'counter_name_str' not in d:
                self.log.warning('SKIP: missing key counter_name_str: {}'.format(d))
                continue
            name_key = d['counter_name_str']
            self._queuing_counter_dict[name_key] = dict()
            for key in d:
                if 'qos_group' in key:
                    self._queuing_counter_dict[name_key][key] = d[key]


    def refresh(self):
        self.info = dict()
        cli = 'show queuing tabular interface {}'.format(self.interface)
        self.show(cli)
        self._get_module_dict()
        self._get_queuing_interface_dict_from_module_dict()
        self.make_info_dict()

    def make_info_dict(self):
        '''
        this creates the main user-facing dictionary
        '''
        self.info = dict()
        self._get_queuing_counter_dict_from_queuing_interface_dict()
        if len(self._queuing_counter_dict) == 0:
            self.log.debug('returning empty self.info due to empty self._queuing_counter_dict')
            return
        self.info = deepcopy(self._queuing_counter_dict)


    def verify_qos_group(self, x, parameter='qos_group'):
        verify_set = self.valid_qos_group
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}. Expected one of {}'.format(
            parameter,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def verify_counter_name(self, x, parameter='counter_name'):
        verify_set = self.valid_counter_name
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}. Expected one of {}'.format(
            parameter,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def get_counter(self):
        if self.properties['counter_name'] == None:
            self.log.error('exiting. Set counter_name before calling get_counter()')
            exit(1)
        if self.properties['qos_group'] == None:
            self.log.error('exiting. Set qos_group before calling get_counter()')
            exit(1)
        try:
            return int(self.info[self.counter_name]['qos_group_{}'.format(self.qos_group)])
        except:
            return self.info[self.counter_name]['qos_group_{}'.format(self.qos_group)]

    @property
    def interface(self):
        if self.properties['interface'] == None:
            self.log.error('exiting.  set interface first.')
            exit(1)
        return self.properties['interface']
    @interface.setter
    def interface(self, x):
        self.properties['interface'] = x

    @property
    def qos_group(self):
        if self.properties['qos_group'] == None:
            self.log.error('exiting.  set qos_group first.')
            exit(1)
        return self.properties['qos_group']
    @qos_group.setter
    def qos_group(self, x):
        self.verify_qos_group(x)
        self.properties['qos_group'] = x

    @property
    def counter_name(self):
        if self.properties['counter_name'] == None:
            self.log.error('exiting.  set counter_name first.')
            exit(1)
        return self.properties['counter_name']
    @counter_name.setter
    def counter_name(self, x):
        self.verify_counter_name(x)
        self.properties['counter_name'] = x
