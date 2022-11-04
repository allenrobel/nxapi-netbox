#!/usr/bin/env python3
'''
Name: nxapi_ipv6_nd.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving ipv6 neighbor information 

Example usage:

# prints neighbors in default vrf
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_ipv6_nd import NxapiIpv6Neighbor
# INFO logging to screen, DEBUG logging to file /tmp/script_name.log
log = get_logger('script_name', 'INFO', 'DEBUG')
nx = NxapiIpv6Neighbor('myusername', 'mypassword', '192.168.1.1', log)
nx.nxapi_init(cfg)
nx.vrf = 'default'
nx.refresh()
fmt = '{:<15} {:<20} {:<30} {:<13} {:<10} {:<14} {:<4} {:<10}'
for neighbor in nx.info:
    nx.ipv6_addr = neighbor
    print(fmt.format(
        ip,
        nx.hostname,
        nx.ipv6_addr,
        nx.intf_out,
        nx.time_stamp,
        nx.mac,
        nx.pref,
        nx.owner))
'''
our_version = 103

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiIpv6Neighbor(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._ipv6_addr = None
        self._info = dict()
        self._path_info = list()
        self._pref = None
        self._uptime = None

    def _get_vrf_dict(self):
        '''
        create dictionary self._vrf_dict from the contents of TABLE_vrf

        {
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf-name-out": "default", 
        '''
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        self._vrf_dict = dict()
        try:
            _vrf_list = self._convert_to_list(self.body[0]['TABLE_vrf']['ROW_vrf'])
        except:
            self.log.error('{} early return: [TABLE_vrf][ROW_vrf] not present in self.body[0] {}'.format(self.hostname, self.body[0]))
            return
        for _vrf_dict in _vrf_list:
            if 'vrf-name-out' not in _vrf_dict:
                self.log.debug('{} skipping. vrf-name-out key not in _vrf_dict {}'.format(self.hostname, _vrf_dict))
                continue
            if self.body[0]['TABLE_vrf']['ROW_vrf']['vrf-name-out'] != self.vrf:
                self.log.debug('{} skipping vrf {}'.format(self.hostname, self.body[0]['TABLE_vrf']['ROW_vrf']['vrf-name-out']))
                continue
            else:
                self._vrf_dict = _vrf_dict
                return
        self.log.error('{} early return: vrf {} not found'.format(self.hostname, self.vrf))

    def refresh(self):
        self.cli = 'show ipv6 neighbor'
        self.show(self.cli)
        self.make_info_dict()

    def __get_afi_dict_from_vrf_dict(self):
        '''
        create dictionary

        {
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf-name-out": "default", 
                    "TABLE_afi": {                <<<<<<<<<<<<<<<
                        "ROW_afi": {
                            "afi": "ipv6", 
                            "count": "4", 
                            "TABLE_adj": {
                                "ROW_adj": [
                                    {
                                        "intf-out": "Ethernet1/51", 
                                        "ipv6-addr": "2113:232::48", 
                                        "time-stamp": "00:22:50", 
                                        "mac": "00f2.8bfd.4ebf", 
                                        "pref": "50", 
                                        "owner": "icmpv6"
                                    }, 
                                    {
                                        "intf-out": "Ethernet1/52", 
                                        "ipv6-addr": "2113:232::6c", 
                                        "time-stamp": "00:20:35", 
                                        "mac": "0027.e399.847f", 
                                        "pref": "50", 
                                        "owner": "icmpv6"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        '''
        self._afi_dict = dict()
        if len(self._vrf_dict) == 0:
            self.log.warning('{} returning empty self._afi_dict due to self._vrf_dict() is empty.'.format(self.hostname))
            return

        try:
            _afi_dicts = self._convert_to_list(self._vrf_dict['TABLE_afi']['ROW_afi'])
        except:
            self.log.warning('{} returning empty self._afi_dict due to key [TABLE_afi][ROW_afi] not found in self._vrf_dict {}'.format(self.hostname, self._vrf_dict))
            return
        for _afi_dict in _afi_dicts:
            try:
                _afi = _afi_dict['afi']
            except:
                self.log.debug('{} skipping due to key [afi] not found in _afi_dict {}'.format(self.hostname, _afi_dict))
                continue
            if _afi == 'ipv6':
                self._afi_dict = _afi_dict
                return
        self.log.warning('{} returning empty self._afi_dict due to IPv6 address-family not found in vrf {}'.format(self.vrf))

    def __get_adj_dict_from_afi_dict(self):
        '''
        create dictionary self._adj_dict from the contents of TABLE_adj

        {
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf-name-out": "default", 
                    "TABLE_afi": {
                        "ROW_afi": {
                            "afi": "ipv6", 
                            "count": "4", 
                            "TABLE_adj": {  <<<<<<<<<<<<<<<
                                "ROW_adj": [
                                    {
                                        "intf-out": "Ethernet1/51", 
                                        "ipv6-addr": "2113:232::48", 
                                        "time-stamp": "00:22:50", 
                                        "mac": "00f2.8bfd.4ebf", 
                                        "pref": "50", 
                                        "owner": "icmpv6"
                                    }, 
                                    {
                                        "intf-out": "Ethernet1/52", 
                                        "ipv6-addr": "2113:232::6c", 
                                        "time-stamp": "00:20:35", 
                                        "mac": "0027.e399.847f", 
                                        "pref": "50", 
                                        "owner": "icmpv6"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        '''
        self._adj_dict = dict()
        if len(self._afi_dict) == 0:
            self.log.warning('{} early return: self._afi_dict() is empty.'.format(self.hostname))
            return
        try:
            _adj_dict_list = self._convert_to_list(self._afi_dict['TABLE_adj']['ROW_adj'])
        except:
            self.log.warning('{} early return: key [TABLE_adj][ROW_adj] not found in self._afi_dict {}'.format(self.hostname, self._afi_dict))
            return
        for _adj_dict in _adj_dict_list:
            #self.log.info('got _adj_dict {}'.format(_adj_dict))
            if 'ipv6-addr' not in _adj_dict:
                continue
            self._adj_dict[_adj_dict['ipv6-addr']] = _adj_dict

    def make_info_dict(self):
        '''
        called from self.refresh()
        call all other parsing methods and create self.info from the result
        '''
        self._info = dict()
        self._get_vrf_dict()
        self.__get_afi_dict_from_vrf_dict()
        self.__get_adj_dict_from_afi_dict()
        self._info = self._adj_dict


    @property
    def mac(self):
        try:
            return self._info[self.ipv6_addr]['mac']
        except:
            return 'na'
    @property
    def owner(self):
        try:
            return self._info[self.ipv6_addr]['owner']
        except:
            return 'na'
    @property
    def pref(self):
        try:
            return self._info[self.ipv6_addr]['pref']
        except:
            return 'na'
    @property
    def time_stamp(self):
        try:
            return self._info[self.ipv6_addr]['time-stamp']
        except:
            return 'na'
    @property
    def intf_out(self):
        try:
            return self._info[self.ipv6_addr]['intf-out']
        except:
            return 'na'
    @property
    def info(self):
        return self._info

    @property
    def neighbor_count(self):
        return len(self._info)

    @property
    def ipv6_addr(self):
        return self._ipv6_addr
    @ipv6_addr.setter
    def ipv6_addr(self, x):
        if not self.verify.is_ipv6_address(x):
            self.log.error('early return: ipv6_addr must be a valid ipv6 address.  Got {}'.format(x))
            return
        self._ipv6_addr = x
