#!/usr/bin/env python3
'''
Name: nxapi_forwarding_route_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving FIB ipv4/ipv6 unicast route summary information 

Synopsis:

from general.log import get_logger
from nxapi.nxapi_forwarding_route_summary import NxapiForwardingRouteSummaryIpv4, NxapiForwardingRouteSummaryIpv6

username = 'admin'
password = 'password'
mgmt_ip = '172.22.159.4'
log = get_logger('mylog', 'INFO', 'ERROR')

fib_dict = dict()
fib_dict[4] = dict()
fib_dict[6] = dict()

fib4 = NxapiForwardingRouteSummaryIpv4(username, password, mgmt_ip, log)
fib4_prefixlens = range(0,33)
fib6 = NxapiForwardingRouteSummaryIpv6(username, password, mgmt_ip, log)
fib6_prefixlens = range(0,129)

fib_dict[4]['obj'] = fib4
fib_dict[4]['prefixlens'] = fib4_prefixlens
fib_dict[6]['obj'] = fib6
fib_dict[6]['prefixlens'] = fib6_prefixlens


for version in fib_dict:
    fib = fib_dict[version]['obj']
    prefixlens = fib_dict[version]['prefixlens']
    fib.nxapi_init(cfg)
    fib.vrf = 'default'
    fib.module = 1
    fib.refresh()
    print('{} Total FIB routes'.format(fib.route_count))
    print('{} Total FIB paths'.format(fib.path_count))

    for prefixlen in prefixlens:
        fib.mask_length = prefixlen
        print('{} /{} prefixes'.format(fib.mask_length, prefixlen))

'''
our_version = 111

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiForwardingRouteSummary(NxapiBase):
    '''
    self.info contains the information below in ROW_prefix associated with self.module, self.vrf

    switch# sh forwarding [ipv4 | ipv6] route summary module 1 vrf default | json-pretty
    {
        "TABLE_module": {
            "ROW_module": {
                "module_number": "1", 
                "TABLE_vrf": {
                    "ROW_vrf": {
                        "vrfname": "default", 
                        "tblname": "base", 
                        "TABLE_prefix": {
                            "ROW_prefix": {
                                "TABLE_path": {
                                    "ROW_path": {
                                        "route_count": [
                                            "391", 
                                            "5059", 
                                            "146", 
                                            "472"
                                        ], 
                                        "path_count": "1832", 
                                        "mask_length": [
                                            "8", 
                                            "10", 
                                            "64", 
                                            "127", 
                                            "128"
                                        ], 
                                        "routes_per_mask": [
                                            "1", 
                                            "1", 
                                            "1", 
                                            "238", 
                                            "231"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._module = 1
        self._vrf = 'default'
        #self._module_set_by_user = False

        self.info = dict()
        # returns the number of routes associated with self.info['routes_per_mask'][mask_length]
        # requires the the user first call:
        #    instance.refresh()
        #    instance.mask_length = X, when X is an integer representing the mask length to query
        self._mask_length = -1

    def _get_vrf_dict_from_module_dict(self):
        '''
        Returns a dict().  Empty, if expected keys are not present.  Else, containing everything in TABLE_vrf and below.
        Note: show forwarding ip route a.b.c.d/e detail does not contain a vrf name in TABLE_vrf/ROW_vrf
        Just pass along whatever the contents of the first element, _vrf_list[0]
        '''
        self._vrf_dict = dict()
        _list = self._get_table_row('vrf', self._module_dict)
        if _list == False:
            return
        self._vrf_dict = _list[0]


    def _get_prefix_dict_from_vrf_dict(self):
        '''
        "TABLE_vrf": {
            "ROW_vrf": {
                "vrf_name_out": "default", 
                "table_name": "base", 
                "TABLE_prefix": {  <<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    "ROW_prefix": {
                        "TABLE_path": {
                            "ROW_path": {
                                "route_count": [
                                    "997", 
                                    "927688", 
                                    "36127", 
                                    "24063"
                                ], 
                                "path_count": "60085", 
                                "mask_length": [
                                    "8", 
                                    "9", 
                                    "24", 
                                    "27", 
                                    "29", 
                                    "30", 
                                    "31", 
                                    "32"
                                ], 
                                "routes_per_mask": [
                                    "2", 
                                    "1", 
                                    "2", 
                                    "24000", 
                                    "4", 
                                    "9", 
                                    "1", 
                                    "44"
                                ]
                            }
                        }
                    }
                }
            }
        }
        '''
        self._prefix_dict = dict()
        if len(self._vrf_dict) == 0:
            self.log.debug('{} early return due to self._vrf_dict() is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('prefix', self._vrf_dict)
        if _list == False:
            return
        if len(_list) != 1:
            self.log.debug('{} early return due to unexpected length of _list. Expected length 1. _list {} '.format(
                self.hostname,
                len(_list),
                _list))
            return
        self._prefix_dict = _list[0]

    def _get_path_dict_from_prefix_dict(self):
        '''
        '''
        self._path_dict = dict()

        _list = self._get_table_row('path', self._prefix_dict)
        if _list == False:
            return
        if len(_list) != 1:
            self.log.debug('{} early return due to unexpected length of _list. Expected length 1. _list {} '.format(
                self.hostname,
                len(_list),
                _list))
            return
        self._path_dict = _list[0]

    def _get_route_counts_from_path_dict(self):
        '''
        "TABLE_path": {
            "ROW_path": {
                "route_update_count": "119", 
                "route_insert_count": "42300", 
                "route_delete_count": "0", 
                "route_count": "42264", 
                "path_count": "674754", 
        '''
        key_map = dict()
        key_map['route_update_count'] = 'cumulative_route_updates'
        key_map['route_insert_count'] = 'cumulative_route_inserts'
        key_map['route_delete_count'] = 'cumulative_route_deletes'
        key_map['route_count'] = 'route_count'
        key_map['path_count'] = 'path_count'
        missing_keys = list()
        for key in key_map:
            mapped_key = key_map[key]
            try:
                self.info[mapped_key] = int(self._path_dict[key])
            except:
                missing_keys.append(key)
        if len(missing_keys) != 0:
            self.log.debug('{} early return due to missing keys: {}'.format(
                self.hostname,
                ','.join(missing_keys)))
            return
        self.log.debug('self.info {}'.format(self.info))

    def _get_mask_list_from_path_dict(self):
        '''
        '''
        self._mask_list = list()

        _list = self._get_table_row('mask', self._path_dict)
        if _list == False:
            return
        self._mask_list = _list

    def _get_mask_info_from_mask_list(self):
        '''
        This adds the following key to self.info['routes_per_mask']
        self.info['routes_per_mask'] is keyed on mask_length, converted to integer
        The values are the associated routes_per_mask value for a given mask_length, converted to integer
        For example, based on the JSON below, self.info would contain:
           self.info['routes_per_mask'][8] = 2
           self.info['routes_per_mask'][9] = 1
           self.info['routes_per_mask'][24] = 2
           self.info['routes_per_mask'][27] = 24000
           self.info['routes_per_mask'][29] = 4
           self.info['routes_per_mask'][30] = 9
           self.info['routes_per_mask'][31] = 1
           self.info['routes_per_mask'][32] = 44

        NEW format: as of (at least) 9.3(7)

        "TABLE_path": {
            "ROW_path": {
                "route_update_count": "2525", 
                "route_insert_count": "1533", 
                "route_delete_count": "1432", 
                "route_count": "91", 
                "path_count": "91", 
                "TABLE_mask": {
                    "ROW_mask": [
                        {
                            "mask_length": "8", 
                            "routes_per_mask": "1"
                        }, 
                        {
                            "mask_length": "31", 
                            "routes_per_mask": "29"
                        }, 
                        {
                            "mask_length": "32", 
                            "routes_per_mask": "61"
                        }
                    ]
                }
            }
        }


        '''

        if len(self._mask_list) == 0:
            self.log.debug('{} early return due to mask_list is 0'.format(
                self.hostname))
            return
        for item_dict in self._mask_list:
            if 'mask_length' not in item_dict:
                self.log.debug('{} early return due to key [mask_length] not found in item_dict {}'.format(
                    self.hostname,
                    item_dict))
                return
            if 'routes_per_mask' not in item_dict:
                self.log.debug('{} early return due to key [routes_per_mask] not found in item_dict {}'.format(
                    self.hostname,
                    item_dict))
                return

        self.info['routes_per_mask'] = dict()
        for item_dict in self._mask_list:
            mask_length = int(item_dict['mask_length'])
            route_count = int(item_dict['routes_per_mask'])
            self.info['routes_per_mask'][mask_length] = route_count
        self.log.debug('Got self.info {}'.format(self.info))

    def refresh(self):
        self.info = dict()
        self.cli = 'show forwarding ipv{} route summary vrf {} module {}'.format(self.ip_version, self.vrf, self.module)
        self.show(self.cli)
        self._get_module_dict()
        self._get_vrf_dict_from_module_dict()
        self.make_info_dict()

    def make_info_dict(self):
        '''
        this creates the main user-facing dictionary
        '''
        self.info = dict()
        self._get_prefix_dict_from_vrf_dict()
        if len(self._prefix_dict) == 0:
            self.log.debug('returning empty self.info due to empty self._prefix_dict')
            return
        self._get_path_dict_from_prefix_dict()
        if len(self._path_dict) == 0:
            self.log.debug('returning empty self.info due to empty self._path_dict')
            return
        # the following add keys to self.info
        self._get_route_counts_from_path_dict()
        self._get_mask_list_from_path_dict()
        self._get_mask_info_from_mask_list()

    @property
    def path_count(self):
        try:
            return self.info['path_count']
        except:
            return -1

    @property
    def route_count(self):
        try:
            return self.info['route_count']
        except:
            return -1

    @property
    def route_updates(self):
        try:
            return self.info['cumulative_route_updates']
        except:
            return -1

    @property
    def route_inserts(self):
        try:
            return self.info['cumulative_route_inserts']
        except:
            return -1

    @property
    def route_deletes(self):
        try:
            return self.info['cumulative_route_deletes']
        except:
            return -1

    @property
    def mask_length(self):
        '''
        allows the user to query a specific mask_length for the number of routes associated with that mask_length
        '''
        try:
            return self.info['routes_per_mask'][self._mask_length]
        except:
            return -1
    @mask_length.setter
    def mask_length(self, _x):
        try:
            self._mask_length = int(str(_x))
        except:
            self.log.debug('invalid mask_length {}. Do nothing'.format(_x))


class NxapiForwardingRouteSummaryIpv4(NxapiForwardingRouteSummary):
    '''
    See superclass for details
    '''
    def __init__(self, username, password, mgmt_ip, loglevel):
        super().__init__(username, password, mgmt_ip, loglevel)
        self.ip_version = 4

class NxapiForwardingRouteSummaryIpv6(NxapiForwardingRouteSummary):
    '''
    See superclass for details
    '''
    def __init__(self, username, password, mgmt_ip, loglevel):
        super().__init__(username, password, mgmt_ip, loglevel)
        self.ip_version = 6
