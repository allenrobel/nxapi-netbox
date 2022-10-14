#!/usr/bin/env python3
'''
Name: nxapi_interface_egress_queuing.py
Author: Allen Robel (arobel@cisco.com)
Description: Class containing methods for retrieving interface queuing counters

Synopsis:

'''
our_version = 103

# standard libraries
from copy import deepcopy
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiInterfaceEgressQueuing(NxapiBase):
    '''
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)

        self._interface = None
        self.info = dict()

        self.properties = dict()
        self.properties['interface'] = None
        self.properties['qos_group'] = None
        self.properties['unit'] = None

        self.valid_stat_type = set()
        self.valid_stat_type.add('tx')
        self.valid_stat_type.add('ecn')
        self.valid_stat_type.add('tail_drop')
        self.valid_stat_type.add('q_depth')
        self.stat_types = list(sorted(self.valid_stat_type))

        self.stat_type_map = dict()
        self.stat_type_map['tail_drop'] = 'WRED/AFD & Tail Drop'
        self.stat_type_map['ecn'] = 'ECN'
        self.stat_type_map['tx'] = 'Tx'
        self.stat_type_map['q_depth'] = 'Q Depth'
        self.stat_type_map['WRED/AFD & Tail Drop'] = 'tail_drop'
        self.stat_type_map['ECN'] = 'ecn'
        self.stat_type_map['Tx'] = 'tx'
        self.stat_type_map['Q Depth'] = 'q_depth'

        self.valid_unit = set()
        self.valid_unit.add('packets')
        self.valid_unit.add('bytes')
        self.units = list(sorted(self.valid_unit))

        self.unit_map = dict()
        self.unit_map['packets'] = 'Pkts'
        self.unit_map['bytes'] = 'Byts'
        self.unit_map['Pkts'] = 'packets'
        self.unit_map['Byts'] = 'bytes'

        self.valid_counter_name = set()
        self.valid_counter_name.add('eq-stat-type')
        self.valid_counter_name.add('eq-stat-units')
        self.valid_counter_name.add('eq-uc-stat-value')
        self.valid_counter_name.add('eq-mc-stat-value')

        self.counter_names = sorted(self.valid_counter_name)

        self.valid_protocol = set()
        self.valid_protocol.add('uc')
        self.valid_protocol.add('mc')
        self.protocols = sorted(self.valid_protocol)

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

    def make_dict_orig(self,key):
        d = dict()
        d[key] = dict()
        for stat_type in self.stat_types:
            d[key][stat_type] = dict()
            for unit in self.valid_unit:
                d[key][stat_type][unit] = dict()
                d[key][stat_type][unit]['uc'] = None
                d[key][stat_type][unit]['mc'] = None
        return deepcopy(d)

    def make_dict(self):
        d = dict()
        for stat_type in self.stat_types:
            d[stat_type] = dict()
            for unit in self.valid_unit:
                d[stat_type][unit] = dict()
                d[stat_type][unit]['uc'] = 'na'
                d[stat_type][unit]['mc'] = 'na'
        return deepcopy(d)

    def get_stat_type(self,x):
        if x in self.stat_type_map:
            return self.stat_type_map[x]
        return 'na'
    def get_stat_unit(self,x):
        if x in self.unit_map:
            return self.unit_map[x]
        return 'na'
    def get_stat_value(self,x):
        if x == None:
            return 'na'
        return x

    def _get_qosgrp_egress_stats_entry(self, d, key):
        d1 = self.make_dict()
        l = self._get_table_row('qosgrp_egress_stats_entry', d)
        if l == False:
            return d1
        for d2 in l:
            stat_type = self.get_stat_type(d2['eq-stat-type'])
            unit = self.get_stat_unit(d2['eq-stat-units'])
            d1[stat_type][unit]['uc'] = self.get_stat_value(d2['eq-uc-stat-value'])
            d1[stat_type][unit]['mc'] = self.get_stat_value(d2['eq-mc-stat-value'])
        return deepcopy(d1)

    def get_name_key(self,x):
        if 'CONTROL QOS GROUP' in x:
            return 'cpu'
        elif 'SPAN QOS GROUP' in x:
            return 'span'
        else:
            return x

    def _get_qosgrp_egress_stats_from_queuing_interface_dict(self):
        '''
        TABLE_qosgrp_egress_stats
        Populates a dict(), which will be empty if expected keys are not present.
        Else, will contain everything in TABLE_queuing_interface and below.
        '''
        self._qosgrp_egress_stats_dict = dict()
        _list = self._get_table_row('qosgrp_egress_stats', self._queuing_interface_dict)
        if _list == False:
            return
        for d in _list:
            if 'eq-qosgrp' not in d:
                self.log.warning('SKIP: missing key eq-qosgrp: {}'.format(d))
                continue
            key = self.get_name_key(d['eq-qosgrp'])
            self._qosgrp_egress_stats_dict[key] = self._get_qosgrp_egress_stats_entry(d, key)
            #print('DEBUG self._qosgrp_egress_stats_dict[{}] {}'.format(name_key, self._qosgrp_egress_stats_dict[name_key]))


    def refresh(self):
        self.info = dict()
        cli = 'show queuing interface {}'.format(self.interface)
        self.show(cli)
        self._get_module_dict()
        self._get_queuing_interface_dict_from_module_dict()
        self._get_qosgrp_egress_stats_from_queuing_interface_dict()
        self.make_info_dict()

    def make_info_dict(self):
        '''
        this creates the main user-facing dictionary
        '''
        self.info = dict()
        if len(self._qosgrp_egress_stats_dict) == 0:
            self.log.debug('returning empty self.info due to empty self._qosgrp_egress_stats_dict')
            return
        self.info = deepcopy(self._qosgrp_egress_stats_dict)

    def verify_qos_group(self, x, parameter='qos_group'):
        verify_set = self.valid_qos_group
        try:
            x = int(x)
        except:
            pass
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}: {}. Expected one of {}'.format(
            parameter,
            x,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def verify_stat_type(self, x, parameter='stat_type'):
        verify_set = self.valid_stat_type
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}: {}. Expected one of {}'.format(
            parameter,
            x,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def verify_unit(self, x, parameter='unit'):
        verify_set = self.valid_unit
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}: {}. Expected one of {}'.format(
            parameter,
            x,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def verify_protocol(self, x, parameter='protocol'):
        verify_set = self.valid_protocol
        if x in verify_set:
            return
        self.log.error('exiting. Invalid {}: {}. Expected one of {}'.format(
            parameter,
            x,
            ','.join([str(x) for x in verify_set])))
        exit(1)

    def get_counter(self, counter):
        if self.properties['qos_group'] == None:
            self.log.error('exiting. Set qos_group before retrieving counters')
            self.log.error('valid values are: {}'.format(','.join(self.qos_groups)))
            exit(1)
        if self.properties['unit'] == None:
            self.log.error('exiting. Set unit before retrieving counters')
            self.log.error('valid values are: {}'.format(','.join(self.units)))
            exit(1)
        if self.properties['protocol'] == None:
            self.log.error('exiting. Set protocol before retrieving counters')
            self.log.error('valid values are: {}'.format(','.join(self.protocols)))
            exit(1)
        try:
            return int(self.info[str(self.qos_group)][counter][self.unit][self.protocol])
        except:
            try:
                return self.info[str(self.qos_group)][counter][self.unit][self.protocol]
            except:
                return 'na'

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
    def unit(self):
        if self.properties['unit'] == None:
            self.log.error('exiting.  set unit first.')
            exit(1)
        return self.properties['unit']
    @unit.setter
    def unit(self, x):
        self.verify_unit(x)
        self.properties['unit'] = x

    @property
    def protocol(self):
        if self.properties['protocol'] == None:
            self.log.error('exiting.  set protocol first.')
            exit(1)
        return self.properties['protocol']
    @protocol.setter
    def protocol(self, x):
        self.verify_protocol(x)
        self.properties['protocol'] = x

    @property
    def ecn(self):
        return self.get_counter('ecn')
    @property
    def tx(self):
        return self.get_counter('tx')
    @property
    def q_depth(self):
        return self.get_counter('q_depth')
    @property
    def tail_drop(self):
        return self.get_counter('tail_drop')

    