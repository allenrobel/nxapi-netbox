#!/usr/bin/env python3
our_version = 108
'''
Name: nxapi_forwarding_route_unicast.py
Author: Allen Robel (arobel@cisco.com)
Description: NXAPI: Classes containing methods for retrieving ipv4/ipv6 unicast fib information 

Synopsis:

from nxapi.nxapi_forwarding_route_unicast import NxapiForwardingRouteUnicastIpv4
from log import get_logger

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

log = get_logger('nxapi_forwarding_example', 'INFO', 'DEBUG')
username = 'admin'
password = 'foo'
mgmt0_ip = '1.1.1.1'
ipv4 = NxapiForwardingRouteUnicastIpv4(username,password,mgmt0_ip,log)
ipv4.prefix = '4.0.0.0/8'
ipv4.vrf = 'default'
ipv4.module = 1
ipv4.refresh()
print_dict(ipv4.prefix_info)
print_dict(ipv4.path_info)
'''

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiForwardingRouteUnicast(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._prefix = None
        self._prefix_info = dict()
        self._path_info = list()

    def _get_vrf_dict_from_module_dict(self):
        '''
        Returns a dict().  Empty, if expected keys are not present.  Else, containing everything in TABLE_vrf and below.
        Note: show forwarding ip route a.b.c.d/e detail does not contain a vrf name in TABLE_vrf/ROW_vrf
        Just pass along whatever the contents of the first element, _vrf_list[0]
        {
        "TABLE_vrf": {
            "ROW_vrf": {
                "TABLE_prefix": {
                    "ROW_prefix": {
                        "ip_prefix": "10.10.10.2/32", 
                        "num_paths": "1", 
                        "TABLE_path": {
                        "ROW_path": [
                            {
                                "ip_nexthop": "172.18.2.22", 
                                "ifname": "Ethernet1/53"
                            }, 
                            {
                                "ip_nexthop": "172.18.2.46", 
                                "ifname": "Vlan10"
                            }
                        ]
                        }
                    }
                }
            }
        }
        '''
        self._vrf_dict = dict()
        _list = self._get_table_row('vrf', self._module_dict)
        if _list == False:
            return
        self._vrf_dict = _list[0]


class NxapiForwardingRouteUnicastIpv4(NxapiForwardingRouteUnicast):
    '''
    Creates two items:

    1. a dictionary, self._prefix_info
    2. a list of dictionaries, self._path_info

    self._prefix_info contains the information below in ROW_prefix associated with self.module, self.vrf, self.prefix
    self._path_info contains the information below from ROW_path

    ts_101# sh forwarding ip route 10.10.10.2/32 detail vrf default module 1 | json-pretty 
    {
        "TABLE_module": {
            "ROW_module": {
                "module_number": "1", 
                "TABLE_vrf": {
                    "ROW_vrf": {
                        "TABLE_prefix": {
                            "ROW_prefix": {
                                "ip_prefix": "10.10.10.2/32", 
                                "num_paths": "1", 
                                "TABLE_path": {
                                "ROW_path": [
                                    {
                                        "ip_nexthop": "172.18.2.22", 
                                        "ifname": "Ethernet1/53"
                                    }, 
                                    {
                                        "ip_nexthop": "172.18.2.46", 
                                        "ifname": "Vlan10"
                                    }
                                ]
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    ts_101# 
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.ip_version = 4

    def refresh(self):
        if self.module == None:
            self.log.error('Exiting. Please call <instance>.module = X first')
            exit(1)
        if self.prefix == None:
            self.log.error('Exiting. Please call <instance>.prefix = "a.b.c.d/e" first')
            exit(1)
        if self.vrf == None:
            self.log.error('Exiting. Please call <instance>.vrf = "myvrf" first')
            exit(1)
        self.cli = 'sh forwarding ipv4 route {} detail vrf {} module {}'.format(self.prefix, self.vrf, self.module)
        self.show(self.cli)
        self._get_module_dict()
        self._get_vrf_dict_from_module_dict()
        self.make_prefix_info_dict()

    def _get_prefix_dict_from_vrf_dict(self):
        '''
        "TABLE_vrf": {
            "ROW_vrf": {
                "TABLE_prefix": {
                    "ROW_prefix": {
                        "ip_prefix": "10.10.10.2/32", 
                        "num_paths": "1", 
                        "TABLE_path": {
                        "ROW_path": [
                            {
                                "ip_nexthop": "172.18.2.22", 
                                "ifname": "Ethernet1/53"
                            }, 
                            {
                                "ip_nexthop": "172.18.2.46", 
                                "ifname": "Vlan10"
                            }
                        ]
                        }
                    }
                }
            }
        }
        '''
        self._prefix_dict = dict()

        _list = self._get_table_row('prefix', self._vrf_dict)
        if _list == False:
            return
        for _dict in _list:
            try:
                _prefix = _dict['ip_prefix']
            except:
                self.log.warning('{} skipping due to key [ip_prefix] not found in _dict {}'.format(self.hostname, _dict))
                continue
            if _prefix == self.prefix:
                self._prefix_dict = _dict
                return
        self.log.warning('{} returning empty self._prefix_dict due to prefix {} not found in vrf {} module {}'.format(self.hostname, self.prefix, self.vrf, self.module))


    def _get_path_dicts_from_prefix_info(self):
        '''
        "TABLE_prefix": {
            "ROW_prefix": {
                "ip_prefix": "10.10.10.2/32", 
                "num_paths": "1", 
                "TABLE_path": {
                "ROW_path": [   <<<<
                    {
                        "ip_nexthop": "172.18.2.22", 
                        "ifname": "Ethernet1/53"
                    }, 
                    {
                        "ip_nexthop": "172.18.2.46", 
                        "ifname": "Vlan10"
                    }
                ]
                }
            }
        }

        ROW_path can also be a single dict()
        _get_table_row() does the right thing and returns this
        single dict() in a list e.g. [{}]

        {
            "module_number": "27", 
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf_name_out": "default", 
                    "table_name": "base", 
                    "TABLE_prefix": {
                        "ROW_prefix": {
                            "ip_prefix": "10.231.0.6/31", 
                            "TABLE_path": {
                                "ROW_path": {
                                    "special": "Attached", 
                                    "ifname": "Ethernet1/2"
                                }
                            }
                        }
                    }
                }
            }
        }

        '''
        self._path_info = list()
        _list = self._get_table_row('path', self._prefix_info)
        if _list == False:
            return
        self._path_info = _list


    def make_prefix_info_dict(self):
        '''
        "TABLE_prefix": {
            "ROW_prefix": {
                "ip_prefix": "10.10.10.2/32", 
                "num_paths": "1", 
                "TABLE_path": {
                "ROW_path": [
                    {
                        "ip_nexthop": "172.18.2.22", 
                        "ifname": "Ethernet1/53"
                    }, 
                    {
                        "ip_nexthop": "172.18.2.46", 
                        "ifname": "Vlan10"
                    }
                ]
                }
            }
        }
        '''
        self._prefix_info = dict()
        self._get_prefix_dict_from_vrf_dict()
        self._prefix_info = self._prefix_dict
        self._get_path_dicts_from_prefix_info()

    @property
    def prefix(self):
        return self._prefix
    @prefix.setter
    def prefix(self,_x):
        if not self.verify.is_ipv4_network(_x):
            self.log.error('Exiting. prefix must be a valid ipv4 prefix in a.b.c.d/e format.  Got {}'.format(_x))
            exit(1)
        self._prefix = _x

    @property
    def prefix_info(self):
        '''
        Assuming refresh() was successful, prefix_info contains the same information
        as the group of convenience properties for self.prefix_info below.
        '''
        return self._prefix_info

    # convenience properties to pull individual values from self.prefix_info
    @property
    def ip_prefix(self):
        try:
            return self._prefix_info['ip_prefix']
        except:
            return 'na'

    @property
    def num_paths(self):
        try:
            return self._prefix_info['num_paths']
        except:
            return 'na'

    @property
    def path_info(self):
        '''
        Assuming refresh() was successful, path_info returns a list of dictionaries.
        self._prefix_info['TABLE_path']['ROW_path']
        '''
        return self._path_info
