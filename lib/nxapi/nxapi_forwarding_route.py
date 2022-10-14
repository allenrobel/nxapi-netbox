#!/usr/bin/env python3
'''
DEPRECATED!  PLEASE USE nxapi_forwarding_route_unicast.py instead.

Name: nxapi_forwarding_route.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving ipv4/ipv6 fib information

Synopsis:

script_name = 'test_nxapi_forwarding_route'
our_version = 100

from log import get_logger
from nxapi.nxapi_forwarding_route import NxapiForwardingRouteIpv4

mgmt_ip = '172.22.159.4'
log = get_logger('my_script', cfg.loglevel, 'DEBUG')
# note cfg.sid is not being used here. instead we hardcode mgmt_ip
ipv4 = NxapiForwardingRouteIpv4(cfg.username, cfg.password, mgmt_ip, log)
ipv4.nxapi_init(cfg)
ipv4.prefix = '0.0.0.0/0'
ipv4.vrf = 'default'
ipv4.module = 2
ipv4.refresh()
print('hostname {} prefix {} num_paths {}'.format(ipv4.hostname, ipv4.prefix, ipv4.num_paths))
for path in ipv4.path_info:
    print('  next_hop {:<16} -> {:<20}'.format(path['ip_nexthop'], path['ifname']))


TODO: 
   1. Add subclass NxapiForwardingRouteIpv6()
   2. Complete the remaining convenience properties

NOTES:
   1. self.verify is inherited from NxapiBase
   2. self.vrf is inherited from NxapiBase

'''
our_version = 103

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiForwardingRoute(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        # self.vrf is inherited from NxapiBase
        self._module = None
        self._prefix = None
        self._num_paths = 0

    def _get_vrf_dict_from_module_dict(self):
        '''
        {
            "module_number": "1", 
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf_name_out": "default", 
        '''
        self._vrf_dict = dict()
        try:
            _vrf_list = self._convert_to_list(self._module_dict['TABLE_vrf']['ROW_vrf'])
        except:
            self.log.error('{} early return: [TABLE_vrf][ROW_vrf] not present in self._module_dict {}'.format(self.hostname, self._module_dict))
            return
        for _vrf_dict in _vrf_list:
            if 'vrf_name_out' not in _vrf_dict:
                self.log.debug('{} skipping. vrf_name_out key not in _vrf_dict {}'.format(self.hostname, _vrf_dict))
                continue
            if _vrf_dict['vrf_name_out'] != self.vrf:
                self.log.debug('{} skipping vrf {}'.format(self.hostname, _vrf_dict['vrf_name_out']))
                continue
            else:
                self._vrf_dict = _vrf_dict
                return
        self.log.error('{} early return: vrf {} not found'.format(self.hostname, self.vrf))

        @property
        def module(self):
            return self._module
        @module.setter
        def module(self,_x):
            if not self.verify.is_int(_x):
                self.log.error('early return: module must be an integer.  Got {}'.format(_x))
                return
            self._module = int(_x)

class NxapiForwardingRouteIpv4(NxapiForwardingRoute):
    '''
    returns the following:

    self.prefix_info  - a dictionary consisting of information in TABLE_prefix below
    self.path_info - a list of dictionaries, each consisting of information in ROW_path below

    oz-201v6# sh forwarding ipv4 route 10.239.0.24/32 | json-pretty
    {
        "TABLE_module": {
            "ROW_module": [
                {
                    "module_number": "1", 
                    "TABLE_vrf": {
                        "ROW_vrf": {
                            "vrf_name_out": "default", 
                            "table_name": "base", 
                            "TABLE_prefix": {                       <<<< self.prefix_info
                                "ROW_prefix": {
                                    "ip_prefix": "10.239.0.24/32", 
                                    "TABLE_path": {
                                        "ROW_path": [               <<<< self.path_info
                                            {
                                                "ip_nexthop": "2112:232::20", 
                                                "ifname": "Ethernet1/3"
                                            }, 
                                            {
                                                "ip_nexthop": "2112:232::22", 
                                                "ifname": "Ethernet1/4"
                                            }, 
                                            {
                                                "ip_nexthop": "2112:232::24", 
                                                "ifname": "Ethernet2/3"
                                            }, 
                                            {
                                                "ip_nexthop": "2112:232::26", 
                                                "ifname": "Ethernet2/4"
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._prefix_info = dict()
        self._path_info = list()
        self._pref = None
        self._uptime = None

    def refresh(self):
        if self.prefix == None:
            self.log.error('early return:  Please call <instance>.prefix = "a.b.c.d/e" first')
            return
        self.cli = 'show forwarding ipv4 route {}'.format(self.prefix)
        self.show(self.cli)
        self._get_module_dict()
        self._get_vrf_dict_from_module_dict()
        self.make_prefix_info_dict()


    def __get_prefix_dict_from_vrf_dict(self):
        '''
        "ROW_vrf": {
            "vrf_name_out": "default", 
            "table_name": "base", 
            "TABLE_prefix": {                       <<<< self.prefix_info
                "ROW_prefix": {
                    "ip_prefix": "10.239.0.24/32", 
                    "TABLE_path": {
                        "ROW_path": [               <<<< self.path_info
                            {
                                "ip_nexthop": "2112:232::20", 
                                "ifname": "Ethernet1/3"
                            }, 
                            {
                                "ip_nexthop": "2112:232::22", 
                                "ifname": "Ethernet1/4"
                            }, 
                            {
                                "ip_nexthop": "2112:232::24", 
                                "ifname": "Ethernet2/3"
                            }, 
                            {
                                "ip_nexthop": "2112:232::26", 
                                "ifname": "Ethernet2/4"
                            }
                        ]
                    }
                }
            }
        }
        '''
        self._prefix_dict = dict()
        if len(self._vrf_dict) == 0:
            self.log.warning('{} early return: self._vrf_dict() is empty.'.format(self.hostname))
            return
        try:
            _prefix_dicts = self._convert_to_list(self._vrf_dict['TABLE_prefix']['ROW_prefix'])
        except:
            self.log.warning('{} early return: key [TABLE_prefix][ROW_prefix] not found in self._vrf_dict {}'.format(self.hostname, self._vrf_dict))
            return
        for _prefix_dict in _prefix_dicts:
            try:
                _prefix = _prefix_dict['ip_prefix']
            except:
                self.log.debug('{} skipping due to key [ip_prefix] not found in _prefix_dict {}'.format(self.hostname, _prefix_dict))
                continue
            if _prefix == self.prefix:
                self._prefix_dict = _prefix_dict
                return
        self.log.warning('{} early return: IPv4 prefix {} not found in _prefix_dicts {}'.format(self.prefix, _prefix_dicts))

    def _get_path_dicts_from_prefix_info(self):
        self._path_info = list()
        if 'TABLE_path' not in self._prefix_info:
            self.log.warning('{} early return: key [TABLE_path] not found in self.prefix_info {}'.format(self.hostname, self._prefix_info))
            return
        try:
            self._path_info = self._convert_to_list(self._prefix_info['TABLE_path']['ROW_path'])
        except:
            self.log.warning('{} Setting empty self._path_info list() due to key [TABLE_path][ROW_path] not found in self.prefix_info {}'.format(self.hostname, self.prefix_info))
            self._path_info = list()
            return
        self._num_paths = len(self.path_info)

    def make_prefix_info_dict(self):
        '''
        {
        "ipprefix": "172.12.12.12/32", 
        "ucast-nhops": "1", 
        "mcast-nhops": "0", 
        "attached": "false", 
            "TABLE_path": {
                "ROW_path": [
                    {
                        "ipnexthop": "172.18.2.22", 
                        "uptime": "PT17H3M49S", 
                        "pref": "20", 
                        "metric": "0", 
                        "clientname": "bgp-45001", 
                        "type": "external", 
                        "tag": "45000", 
                        "ubest": "true"
                    }, 
                    {
                        "ipnexthop": "172.18.1.4", 
                        "uptime": "PT17H3M49S", 
                        "pref": "200", 
                        "metric": "0", 
                        "clientname": "bgp-45001", 
                        "type": "internal", 
                        "tag": "45000"
                    }
                ]
            }
        }
        '''
        self._prefix_info = dict()
        self._get_module_dict()
        self._get_vrf_dict_from_module_dict()

        self.__get_prefix_dict_from_vrf_dict()
        self._prefix_info = self._prefix_dict
        self._get_path_dicts_from_prefix_info()

    @property
    def pref(self):
        if len(self._path_info) == 0:
            return 'na'
        for path in self._path_info:
            if 'ubest' in path:
                return int(path['pref'])
        return 'na'

    @property
    def prefix_info(self):
        return self._prefix_info
    @property
    def path_info(self):
        return self._path_info
    @property
    def num_paths(self):
        return self._num_paths
    
    @property
    def prefix(self):
        return self._prefix
    @prefix.setter
    def prefix(self,_x):
        if not self.verify.is_ipv4_network(_x):
            self.log.error('early return: prefix must be a valid ipv4 prefix in a.b.c.d/e format.  Got {}'.format(_x))
            return
        self._prefix = _x
