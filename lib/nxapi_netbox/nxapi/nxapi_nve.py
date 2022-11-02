#!/usr/bin/env python3
'''
Name: nxapi_nve.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes for retrieving NVE information 

Synopsis:

See the following scripts in this repo:
   scripts/nve_peers_sid.py
   scripts/nve_interface_sid.py
'''
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

our_version = 109

class NxapiNvePeers(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self._peer_ip = None
        self._if_name = None
        self._peer_state = None
        self._learn_type = None
        self._uptime = None
        self._router_mac = None
        '''
            "ROW_nve_peers": {
                "if-name": "nve1", 
                "peer-ip": "10.10.10.14",  <<< This will be peer-ipv6 for IPv6 VTEP
                "peer-state": "Up", 
                "learn-type": "CP", 
                "uptime": "8w4d", 
                "router-mac": "n/a"
        '''
    def make_info_dict(self):
        '''
        self.info will contain as many entries as there are nv peers and will have the following structure:

        self.info[peer_ip]['if-name']
        self.info[peer_ip]['peer-ip']
        self.info[peer_ip]['peer-state']
        self.info[peer_ip]['learn-type']
        self.info[peer_ip]['uptime']
        self.info[peer_ip]['router-mac']
        '''
        self._info = dict()
        if self.body_length != 1:
            self.log.error('{} v{} early return: unexpected body_length {}'.format(self.hostname, self.lib_version, self.body_length))
            return
        _table = 'TABLE_nve_peers'
        _row = 'ROW_nve_peers'
        try:
            _dict = self.body[0][_table][_row]
        except:
            self.log.error('{} v{} early return: unable to find [{}][{}] in self.body[0] {}'.format(self.hostname, self.lib_version, _table, _row, self.body[0]))
            return

        _peers = self._convert_to_list(_dict)
        for _peer_dict in _peers:
            if 'peer-ip' not in _peer_dict:
                self.log.info('{} v{} skipping. peer-ip key not in _peer_dict {}'.format(self.hostname, self.lib_version, _peer_dict))
                continue
            self._info[_peer_dict['peer-ip']] = _peer_dict
        self.log.debug('self._info {}'.format(self._info))

    def refresh(self):
        self.cli = 'show nve peers'
        self.show()
        self.make_info_dict()

        for _peer in self.info:
            for _key in self.info[_peer]:
                self.log.debug('{} v{} peer {} key {} value {}'.format(self.hostname, self.lib_version, _peer, _key, self.info[_peer][_key]))

    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info
        except:
            return dict()

    def verify_prerequisites(self):
        '''
        used in the @properties below
        '''
        if self._peer_ip == None:
            self.log.error('Exiting. Need to set instance.peer_ip first')
            exit(1)

    @property
    def if_name(self):
        self.verify_prerequisites()
        try:
            return self.info[self.peer_ip]['if-name']
        except:
            return None

    @property
    def peer_state(self):
        self.verify_prerequisites()
        try:
            return self.info[self.peer_ip]['peer-state']
        except:
            return None

    @property
    def learn_type(self):
        self.verify_prerequisites()
        try:
            return self.info[self.peer_ip]['learn-type']
        except:
            return None

    @property
    def uptime(self):
        self.verify_prerequisites()
        try:
            return self.info[self.peer_ip]['uptime']
        except:
            return None

    @property
    def router_mac(self):
        self.verify_prerequisites()
        try:
            return self.info[self.peer_ip]['router-mac']
        except:
            return None

class NxapiNvePeersIpv4(NxapiNvePeers):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)

    @property
    def peer_ip(self):
        self.verify_prerequisites()
        try:
            return self.info[self._peer_ip]['peer-ip']
        except:
            return None
    @peer_ip.setter
    def peer_ip(self,_x):
        if not self.verify.is_ipv4_address(_x):
            self.log.error('Exiting. Expected ipv4 address for peer_ip. Got {}'.format(_x))
            exit(1)
        self._peer_ip = _x


class NxapiNvePeersIpv6(NxapiNvePeers):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)

    def make_info_dict(self):
        '''
        self.info will contain as many entries as there are nv peers and will have the following structure:

        self.info[peer_ip]['if-name']
        self.info[peer_ip]['peer-ip']
        self.info[peer_ip]['peer-state']
        self.info[peer_ip]['learn-type']
        self.info[peer_ip]['uptime']
        self.info[peer_ip]['router-mac']
        '''
        self._info = dict()
        if self.body_length != 1:
            self.log.error('{} v{} early return: unexpected body_length {}'.format(self.hostname, self.lib_version, self.body_length))
            return
        _table = 'TABLE_nve_peers'
        _row = 'ROW_nve_peers'
        try:
            _dict = self.body[0][_table][_row]
        except:
            self.log.error('{} v{} early return: unable to find [{}][{}] in self.body[0] {}'.format(self.hostname, self.lib_version, _table, _row, self.body[0]))
            return

        _peers = self._convert_to_list(_dict)
        for _peer_dict in _peers:
            if 'peer-ipv6' not in _peer_dict:
                self.log.info('{} v{} skipping. peer-ipv6 key not in _peer_dict {}'.format(self.hostname, self.lib_version, _peer_dict))
                continue
            self._info[_peer_dict['peer-ipv6']] = _peer_dict
        self.log.debug('self._info {}'.format(self._info))

    @property
    def peer_ip(self):
        self.verify_prerequisites()
        try:
            return self.info[self._peer_ip]['peer-ipv6']
        except:
            return None
    @peer_ip.setter
    def peer_ip(self,_x):
        if not self.verify.is_ipv6_address(_x):
            self.log.error('Exiting. Expected ipv6 address for peer_ipv6. Got {}'.format(_x))
            exit(1)
        self._peer_ip = _x



class NxapiNveInterface(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version

    def refresh(self):
        self.cli = 'show nve interface nve1 detail'
        self.show()
        self.make_info_dict()

        for _key in self.info:
            self.log.debug('{} v{} key {} value {}'.format(self.hostname, self.lib_version, _key, self.info[_key]))


    def make_info_dict(self):
        self._info = dict()
        if self.body_length != 1:
            self.log.error('{} v{} early return: unexpected body_length {}'.format(self.hostname, self.lib_version, self.body_length))
            return
        _table = 'TABLE_nve_if'
        _row = 'ROW_nve_if'
        if _table not in self.body[0]:
            self.log.warning('{} v{} no {}'.format(self.hostname, self.lib_version, _table))
            return
        try:
            _dict = self.body[0][_table][_row]
        except:
            self.log.error('{} v{} early return: unable to find [{}][{}] in self.body[0] {}'.format(self.hostname, self.lib_version, _table, _row, self.body[0]))
            return
        _dicts = self._convert_to_list(_dict)
        for _dict in _dicts:
            if 'if-name' not in _dict:
                self.log.debug('{} v{} skipping. if-name key not in _nve_if_dict {}'.format(self.hostname, self.lib_version, _dict))
                continue
            self.info[_dict['if-name']] = _dict

    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info
        except:
            return dict()
