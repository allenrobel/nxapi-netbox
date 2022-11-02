#!/usr/bin/env python3
'''
Name: nxapi_bgp_unicast.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving bgp ipv4/ipv6 unicast neighbor information 
'''
our_version = 105

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiBgpUnicast(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._vrf = None
        self._prefix = None
        self._vrf_dict = dict()
        self._afi_dict = dict()
        self._safi_dict = dict()
        self.prefix_dict = dict()

class NxapiBgpUnicastIpv4(NxapiBgpUnicast):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._prefixversion = None
        self._totalpaths = None
        self._bestpathnr = None 
        self._on_newlist = None
        self._on_xmitlist = None
        self._suppressed = None
        self._needsresync = None
        self._locked = None
        self._mpath = None

        self._advertised_to = list()

    def refresh(self):
        if self.prefix == None:
            self.log.error('Exiting. Please call <instance>.prefix = "a.b.c.d/e" first')
            exit(1)
        self.cli = 'show bgp ipv4 unicast {}'.format(self.prefix)
        self.show(self.cli)
        self.log.debug('self.cli {}'.format(self.cli))
        self.make_prefix_info_dict()
        self.make_bestpath_info_dict()
        self.make_advertised_to_list()

    def __get_vrf_dict(self):
        '''
        {
            "TABLE_vrf": {
                "ROW_vrf": {
                    "vrf-name-out": "default", 
        '''
        if self.vrf == None:
            self.log.error('{} Exiting. Please call <instance>.vrf = "myvrf" first'.format(self.hostname))
            exit(1)
        self._vrf_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'vrf-name-out' not in _dict:
                continue
            if _dict['vrf-name-out'] != self.vrf:
                continue
            self._vrf_dict = _dict

    def __get_afi_1_dict_from_vrf_dict(self):
        '''
        sets self._afi_dict() if key 'afi' == '1'

        "TABLE_afi": { <<<<
            "ROW_afi": {
                "afi": "1", <<<<<
                "TABLE_safi": {
                    "ROW_safi": {
                        "safi": "1", 
                        "af-name": "IPv4 Unicast", 
                        "TABLE_rd": {
                            "ROW_rd": {
                                "TABLE_prefix": {
                                    "ROW_prefix": {
                                        "ipprefix": "4.0.0.0/8", 
                                        "prefixversion": "211891", 
                                        "totalpaths": "3", 
                                        "bestpathnr": "2", 
                                        "on-newlist": "false", 
                                        "on-xmitlist": "true", 
                                        "suppressed": "false", 
                                        "needsresync": "false", 
                                        "locked": "false", 
                                        "mpath": "eBGP iBGP", 
                                        "TABLE_path": {
        '''
        self._afi_dict = dict()
        if len(self._vrf_dict) == 0:
            self.log.warning('{} Setting empty self._afi_dict due to self._vrf_dict() is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('afi', self._vrf_dict)
        if _list == False:
            return
        for _dict in _list:
            try:
                _afi = _dict['afi']
            except:
                self.log.debug('{} Skipping due to key [afi] not found in _dict {}'.format(self.hostname, _dict))
                continue
            if _afi == '1':
                self._afi_dict = _dict
                return
        self.log.warning('{} Setting empty self._afi_dict due to unicast afi (1) not found.'.format(self.hostname))


    def __get_safi_1_dict_from_afi_dict(self):

        '''
        sets self._safi_dict() if key 'safi' == '1'

        "TABLE_safi": {
            "ROW_safi": {
                "safi": "1", <<<<
                "af-name": "IPv4 Unicast", 
                "TABLE_rd": {
                    "ROW_rd": {
                        "TABLE_prefix": {
                            "ROW_prefix": {
                                "ipprefix": "4.0.0.0/8", 
                                "prefixversion": "211891", 
                                "totalpaths": "3", 
                                "bestpathnr": "2", 
                                "on-newlist": "false", 
                                "on-xmitlist": "true", 
                                "suppressed": "false", 
                                "needsresync": "false", 
                                "locked": "false", 
                                "mpath": "eBGP iBGP", 
                                "TABLE_path": {
        '''
        self._safi_dict = dict()
        if len(self._afi_dict) == 0:
            self.log.warning('{} Setting empty self._safi_dict due to self._afi_dict() is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('safi', self._afi_dict)
        if _list == False:
            return
        for _dict in _list:
            try:
                _safi = _dict['safi']
            except:
                self.log.debug('{} Skipping due to key [safi] not found in _dict {}'.format(self.hostname, _dict))
                continue
            if _safi == '1':
                self._safi_dict = _dict
                return
        self.log.warning('{} Setting empty self._safi_dict due to unicast safi (1) not found in _list.'.format(self.hostname, _list))


    def __get_rd_list_from_safi_dict(self):

        '''
        sets self._safi_dict() if key 'safi' == '1'

        "TABLE_rd": {  <<<
            "ROW_rd": {
                "TABLE_prefix": {
                    "ROW_prefix": {
                        "ipprefix": "4.0.0.0/8", 
                        "prefixversion": "211891", 
                        "totalpaths": "3", 
                        "bestpathnr": "2", 
                        "on-newlist": "false", 
                        "on-xmitlist": "true", 
                        "suppressed": "false", 
                        "needsresync": "false", 
                        "locked": "false", 
                        "mpath": "eBGP iBGP", 
                        "TABLE_path": {
        '''
        self._rd_list = list()
        if len(self._safi_dict) == 0:
            self.log.warning('{} Setting empty self._rd_list due to self._safi_dict() is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('rd', self._safi_dict)
        if _list == False:
            return
        self._rd_list = _list

    def __get_prefix_dicts_from_rd_list(self):

        '''
        sets self._safi_dict() if key 'safi' == '1'

        "TABLE_rd": {  <<<
            "ROW_rd": {
                "TABLE_prefix": {
                    "ROW_prefix": {
                        "ipprefix": "4.0.0.0/8", 
                        "prefixversion": "211891", 
                        "totalpaths": "3", 
                        "bestpathnr": "2", 
                        "on-newlist": "false", 
                        "on-xmitlist": "true", 
                        "suppressed": "false", 
                        "needsresync": "false", 
                        "locked": "false", 
                        "mpath": "eBGP iBGP", 
                        "TABLE_path": {
        '''
        self._prefix_dicts = list()
        if len(self._rd_list) == 0:
            self.log.warning('{} Setting empty self.prefix_dicts list() due to self._rd_list is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('prefix', self._rd_list[0])
        if _list == False:
            return
        self._prefix_dicts = _list


    def make_prefix_info_dict(self):
        '''
        "TABLE_prefix": {
            "ROW_prefix": {
                "ipprefix": "4.0.0.0/8", 
                "prefixversion": "211891", 
                "totalpaths": "3", 
                "bestpathnr": "2", 
                "on-newlist": "false", 
                "on-xmitlist": "true", 
                "suppressed": "false", 
                "needsresync": "false", 
                "locked": "false", 
                "mpath": "eBGP iBGP", 
                "TABLE_path": {
        '''
        self._prefix_info = dict()
        self.__get_vrf_dict()
        self.__get_afi_1_dict_from_vrf_dict()
        self.__get_safi_1_dict_from_afi_dict()
        self.__get_rd_list_from_safi_dict()
        self.__get_prefix_dicts_from_rd_list()

        if len(self._prefix_dicts) == 0:
            self.log.warning('{} Setting empty self.prefix_info due to empty self._prefix_dicts'.format(self.hostname))
            return
        for _prefix_dict in self._prefix_dicts:
            try:
                _ipprefix = _prefix_dict['ipprefix']
            except:
                self.log.warning('{} Skipping due to key [ipprefix] not found in _prefix_dict {}'.format(self.hostname, _prefix_dict))
                continue
            if _ipprefix == self.prefix:
                self._prefix_info = _prefix_dict
                return
        self.log.warning('{} Setting empty self.prefix_info due to prefix {} not found'.format(self.hostname, self.prefix))


    def make_bestpath_info_dict(self):
        '''
        Sets self.bestpath_info dict().  Will be either an empty, or populated with information about the best path for self.prefix
        '''
        self.bestpath_info = dict()
        _list = self._get_table_row('path', self.prefix_info)
        if _list == False:
            return
        for _dict in _list:
            if 'ubest' in _dict:
                self.bestpath_info = _dict
                return
        self.log.debug('{} Setting empty self.bestpath_info due to no bestpath found in self.prefix_info {}'.format(self.hostname, self.prefix_info))


    def make_advertised_to_list(self):
        '''
         'TABLE_advertisedto': 
             {'ROW_advertisedto': 
                 [
                     {'advertisedto': '172.18.1.4'},
                     {'advertisedto': '172.18.2.22'},
                     {'advertisedto': '172.19.3.3'},
                     {'advertisedto': '172.19.3.4'}]}
        '''
        self._advertised_to = list()
        _list = self._get_table_row('advertisedto', self.prefix_info)
        if _list == False:
            return
        for _dict in _list:
            try:
                self._advertised_to.append(_dict['advertisedto'])
            except:
                self.log.error('{} Skipping. key [advertisedto] not found in _dict {}'.format(self.hostname, _dict))
                continue


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
    def vrf(self):
        return self._vrf
    @vrf.setter
    def vrf(self,_x):
        self._vrf = _x

    @property
    def prefix_info(self):
        '''
        Assuming refresh() was successful, prefix_info contains the same information
        as the group of convenience properties for self.prefix_info below.
        '''
        return self._prefix_info
    # convenience properties to pull individual values from self.prefix_info
    @property
    def prefixversion(self):
        try:
            return self.prefix_info['prefixversion']
        except:
            return 'na'
    @property
    def totalpaths(self):
        try:
            return self.prefix_info['totalpaths']
        except:
            return 'na'
    @property
    def bestpathnr(self):
        try:
            return self.prefix_info['bestpathnr']
        except:
            return 'na'
    @property
    def on_newlist(self):
        try:
            return self.prefix_info['on-newlist']
        except:
            return 'na'
    @property
    def on_xmitlist(self):
        try:
            return self.prefix_info['on-xmitlist']
        except:
            return 'na'
    @property
    def suppressed(self):
        try:
            return self.prefix_info['suppressed']
        except:
            return 'na'
    @property
    def needsresync(self):
        try:
            return self.prefix_info['needsresync']
        except:
            return 'na'
    @property
    def locked(self):
        try:
            return self.prefix_info['locked']
        except:
            return 'na'
    @property
    def mpath(self):
        try:
            return self.prefix_info['mpath'].strip()
        except:
            return 'na'

    # advertised_to properties
    @property
    def advertised_to(self):
        return self._advertised_to
