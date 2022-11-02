#!/usr/bin/env python3
'''
Name: nxapi_rib_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes for retrieving ipv4/ipv6 rib summary information 

This corresponds to the output provided by the following cli:

show ip[v6] route summary vrf <vrf>

Synopsis:

from nxapi_netbox.nxapi.nxapi_rib_summary import NxapiRibSummaryIpv4, NxapiRibSummaryIpv6
from nxapi_netbox.general.log import get_logger

username = 'admin'
password = 'mypassword'
ip = '192.168.1.1'
log = get_logger('my_script', 'INFO', 'DEBUG')

ipv4 = NxapiRibSummaryIpv4(username, password, ip, log)
ipv6 = NxapiRibSummaryIpv6(username, password, ip, log)

ipv4.refresh()
print("{} vrf {} ipv4 routes {}".format(ipv4.hostname, ipv4.vrf_name, ipv4.routes))
print("{} vrf {} ipv4 paths {}".format(ipv4.hostname, ipv4.vrf_name, ipv4.paths))
print("{} vrf {} ipv4 am best paths {}".format(ipv4.hostname, ipv4.vrf_name, ipv4.am_best))
print("{} vrf {} ipv4 local paths {}".format(ipv4.hostname, ipv4.vrf_name, ipv4.local_best))
if 32 in ipv4.prefixes['default']:
    print("{} vrf {} /32 ipv4 prefixes {}".format(ipv4.hostname, ipv4.vrf_name, ipv4.prefixes['default'][32]))

# for ipv6, look in vrf TENANT_1 first
ipv6.vrf = 'TENANT_1'
ipv6.refresh()
print("{} vrf {} ipv6 routes {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.routes))
print("{} vrf {} ipv6 paths {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.paths))
# ipv6 has the same paths/prefixes dictionaries, with the same keys as ipv4
if 127 in ipv6.prefixes['TENANT_1']:
    print("{} vrf {} /127 ipv6 prefixes {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.prefixes['TENANT_1'][127]))


# change vrf from TENANT_1 back to default
ipv6.vrf = 'default'
ipv6.refresh()
print("{} vrf {} ipv6 routes {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.routes))
print("{} vrf {} ipv6 paths {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.paths))
# ipv6 has the same paths/prefixes dictionaries, with the same keys as ipv4
if 127 in ipv6.prefixes['TENANT_1']:
    print("{} vrf {} /127 ipv6 prefixes {}".format(ipv6.hostname, ipv6.vrf_name, ipv6.prefixes['TENANT_1'][127]))

Would produce the following output:

% ./nxapi_rib_summary_example.py 
switch vrf default ipv4 routes 24
switch vrf default ipv4 paths 31
switch vrf default ipv4 am paths 2
switch vrf default ipv4 local paths 6
switch vrf default /32 ipv4 prefixes 20
switch vrf TENANT_1 ipv6 routes 3
switch vrf TENANT_1 ipv6 paths 3
switch vrf TENANT_1 /127 ipv6 prefixes 1
switch vrf default ipv6 routes 3
switch vrf default ipv6 paths 3
switch vrf default /127 ipv6 prefixes 1
%
'''
our_version = 107

# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiRibSummary(NxapiBase):
    '''
    Methods for parsing the JSON below.

    Creates the following dictionaries, all keyed on vrf:
    NOTE: self.summary, self.paths, self.prefixes are all properties returning 
          respective dictionaries self._summary_dict, self._paths_dict, self._prefixes_dict, 
    self.summary[self.vrf]['routes']
    self.summary[self.vrf]['paths']
    self.paths[self.vrf]['am'] = <number of am paths>
    self.paths[self.vrf]['local'] = <number of local paths>
    self.paths[self.vrf]['direct'] = <number of direct paths>
    self.paths[self.vrf]['broadcast'] = <number of broadcast paths>
    self.paths[self.vrf]['bgp-xxxx'] = <number of bgp paths IF PRESENT>
    self.prefixes[self.vrf][<mask_len>] = <number of routes with mask_len>

    switch# show ip route summary vrf TENANT_1 | json-pretty 
    {
        "TABLE_vrf": {
            "ROW_vrf": {
                "vrf-name-out": "TENANT_1", 
                "TABLE_addrf": {
                    "ROW_addrf": {
                        "addrf": "ipv4", 
                        "TABLE_summary": {
                            "ROW_summary": {
                                "routes": "55299", 
                                "paths": "55299", 
                                "TABLE_unicast": {
                                    "ROW_unicast": [
                                        {
                                            "clientnameuni": "local", 
                                            "best-paths": "1536"
                                        },
                                ...etc...
                                "TABLE_route_count": {
                                    "ROW_route_count": [
                                        {
                                            "mask_len": "8", 
                                            "count": "1"
                                        }, 
                                ...etc...
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._prefix_list = list()
        self._summary_dict = dict()
        self._best_paths_dict = dict()
        self._backup_paths_dict = dict()
        self._prefixes_dict = dict()
        # note, self.vrf @property is inherited by NxapiBase()

    def _get_vrf_dict_from_body(self):
        self._vrf_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'vrf-name-out' not in _dict:
                continue
            if self._vrf != _dict['vrf-name-out']:
                continue
            self._vrf_dict = _dict

    def _get_addrf_dict_from_vrf_dict(self):
        self._addrf_dict = dict()
        _list = self._get_table_row('addrf', self._vrf_dict)
        if _list == False:
            return
        self._addrf_dict = _list[0]

    def _get_summary_dict_from_addrf_dict(self):
        self._summary_dict = dict()
        _list = self._get_table_row('summary', self._addrf_dict)
        if _list == False:
            return
        self._summary_dict = _list[0]

    def _get_route_count_list_from_summary_dict(self):
        self._route_count_list = list()
        _list = self._get_table_row('route_count', self._summary_dict)
        if _list == False:
            return
        self._route_count_list = _list

    def _get_unicast_list_from_summary_dict(self):
        self._unicast_list = list()
        _list = self._get_table_row('unicast', self._summary_dict)
        if _list == False:
            return
        self._unicast_list = _list


    def make_prefixes_dict(self):
        '''
        from self._route_count_list populate self._prefixes_dict, keyed on self.vrf,
        self._prefixes_dict structure (as returned by property self.prefixes) is:
            self.prefixes[self.vrf][<mask_len>] = <number of routes with max_len>

            <mask_len> is an int()
        '''
        self._prefix_list = list()
        self._prefixes_dict[self.vrf] = dict()
        for _dict in self._route_count_list:
            try:
                mask_len = int(_dict['mask_len'])
            except:
                self.log.debug('{} early return. Unable to find [mask_len] in {}'.format(self.hostname, _dict))
                return
            self._prefix_list.append(mask_len)
            self._prefixes_dict[self.vrf][mask_len] = _dict['count']

    def make_best_paths_dict(self):
        '''
        from self._unicast_list populate self._best_paths_dict, keyed on self.vrf,
        self._base_paths_dict structure (as returned by property self.best_paths) is:
            self.best_paths[self.vrf]['am'] = <number of am paths>
            self.best_paths[self.vrf]['local'] = <number of local paths>
            self.best_paths[self.vrf]['direct'] = <number of direct paths>
            self.best_paths[self.vrf]['broadcast'] = <number of broadcast paths>
            self.best_paths[self.vrf]['bgp-xxxx'] = <number of bgp paths IF PRESENT>
        '''
        self._best_paths_dict[self.vrf] = dict()

        for _dict in self._unicast_list:
            if 'clientnameuni' not in _dict:
                self.log.debug('{} skipping: unable to find [clientnameuni] in _unicast_list {}'.format(self.hostname, self._unicast_list))
                continue
            if 'best-paths' in _dict:
                self._best_paths_dict[self.vrf][_dict['clientnameuni']] = _dict['best-paths']   
            else:
                self.log.debug('{} skipping: unable to find [best-paths] in _dict {}'.format(self.hostname, _dict))
                continue

    def make_backup_paths_dict(self):
        '''
        from self._unicast_list populate self._paths_dict, keyed on self.vrf,
        self._paths_dict structure (as returned by property self.backup_paths) is:
            self.backup_paths[self.vrf]['am'] = <number of am paths>
            self.backup_paths[self.vrf]['local'] = <number of local paths>
            self.backup_paths[self.vrf]['direct'] = <number of direct paths>
            self.backup_paths[self.vrf]['broadcast'] = <number of broadcast paths>
            self.backup_paths[self.vrf]['bgp-xxxx'] = <number of bgp paths IF PRESENT>
        '''
        self._backup_paths_dict[self.vrf] = dict()

        for _dict in self._unicast_list:
            if 'clientnameuni' not in _dict:
                self.log.debug('{} skipping: unable to find [clientnameuni] in _unicast_list {}'.format(self.hostname, self._unicast_list))
                continue
            if 'backup-paths' in _dict:
                self._backup_paths_dict[self.vrf][_dict['clientnameuni']] = _dict['backup-paths']   
            else:
                self.log.debug('{} skipping: unable to find [backup-paths] in _dict {}'.format(self.hostname, _dict))
                continue

    def get_bgp_instance_from_best_paths_dict(self):
        for key in self.best_paths[self.vrf]:
            if 'bgp' in key:
                return key
        return None

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for _vrf in self.summary:
            self.log.debug('{} self.summary[{}] = {}'.format(self.hostname, _vrf, self.summary[_vrf]))
        for _vrf in self.prefixes:
            self.log.debug('{} self.prefixes[{}] = {}'.format(self.hostname, _vrf, self.prefixes[_vrf]))
        for _vrf in self.best_paths:
            self.log.debug('{} self.best_paths[{}] = {}'.format(self.hostname, _vrf, self.best_paths[_vrf]))
        for _vrf in self.best_paths:
            self.log.debug('{} self.backup_paths[{}] = {}'.format(self.hostname, _vrf, self.backup_paths[_vrf]))

    @property
    def prefix_list(self):
        return self._prefix_list

    @property
    def prefixlen(self):
        return self._prefixlen
    @prefixlen.setter
    def prefixlen(self, _x):
        try:
            x = int(str(_x))
        except:
            self.log.error('Exiting. Expected int() for prefixlen. Got {}'.format(_x))
            exit(1)
        if self.ip_version == 4:
            if x > 32:
                self.log.error('Exiting. Expected int() <= 32 for ipv4 prefixlen. Got {}'.format(x))
                exit(1)
        if self.ip_version == 6:
            if x > 128:
                self.log.error('Exiting. Expected int() <= 128 for ipv6 prefixlen. Got {}'.format(x))
                exit(1)
        self._prefixlen = x

    @property
    def prefix(self):
        return self._prefixes_dict[self.vrf][self.prefixlen]
    
    @property
    def best_paths(self):
        return self._best_paths_dict

    @property
    def backup_paths(self):
        return self._backup_paths_dict

    @property
    def prefixes(self):
        return self._prefixes_dict

    @property
    def summary(self):
        return self._summary_dict


    @property
    def routes(self):
        try:
            return self.summary['routes']
        except:
            return -1

    @property
    def paths(self):
        try:
            return self.summary['paths']
        except:
            return -1

    @property
    def am_best(self):
        try:
            return self.best_paths[self.vrf]['am']
        except:
            return -1

    @property
    def am_backup(self):
        try:
            return self.backup_paths[self.vrf]['am']
        except:
            return -1

    @property
    def local_best(self):
        try:
            return self.best_paths[self.vrf]['local']
        except:
            return -1

    @property
    def local_backup(self):
        try:
            return self.backup_paths[self.vrf]['local']
        except:
            return -1

    @property
    def direct_best(self):
        try:
            return self.best_paths[self.vrf]['direct']
        except:
            return -1

    @property
    def direct_backup(self):
        try:
            return self.backup_paths[self.vrf]['direct']
        except:
            return -1

    @property
    def discard_best(self):
        try:
            return self.best_paths[self.vrf]['discard']
        except:
            return -1

    @property
    def discard_backup(self):
        try:
            return self.backup_paths[self.vrf]['discard']
        except:
            return -1

    @property
    def broadcast_best(self):
        try:
            return self.best_paths[self.vrf]['broadcast']
        except:
            return -1

    @property
    def broadcast_backup(self):
        try:
            return self.backup_paths[self.vrf]['broadcast']
        except:
            return -1

    @property
    def bgp_best(self):
        bgp_instance = self.get_bgp_instance_from_best_paths_dict()
        if bgp_instance == None:
            return -1
        try:
            return self.best_paths[self.vrf][bgp_instance]
        except:
            return -1

    @property
    def bgp_backup(self):
        bgp_instance = self.get_bgp_instance_from_best_paths_dict()
        if bgp_instance == None:
            return -1
        try:
            return self.backup_paths[self.vrf][bgp_instance]
        except:
            return -1

class NxapiRibSummaryIpv4(NxapiRibSummary):
    '''
    retrieve ipv4 route summary information
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.ip_version = 4

    def refresh(self):
        self.cli = 'show ip route summary vrf {}'.format(self.vrf)
        self.show(self.cli)
        self._get_vrf_dict_from_body()
        self._get_addrf_dict_from_vrf_dict()
        self._get_summary_dict_from_addrf_dict()
        self._get_route_count_list_from_summary_dict()
        self._get_unicast_list_from_summary_dict()
        self.make_prefixes_dict()
        self.make_best_paths_dict()
        self.make_backup_paths_dict()

class NxapiRibSummaryIpv6(NxapiRibSummary):
    '''
    retrieve ipv6 route summary information
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.ip_version = 6

    def refresh(self):
        self.cli = 'show ipv6 route summary vrf {}'.format(self.vrf)
        self.show(self.cli)
        self._get_vrf_dict_from_body()
        self._get_addrf_dict_from_vrf_dict()
        self._get_summary_dict_from_addrf_dict()
        self._get_route_count_list_from_summary_dict()
        self._get_unicast_list_from_summary_dict()
        self.make_prefixes_dict()
        self.make_best_paths_dict()
        self.make_backup_paths_dict()
