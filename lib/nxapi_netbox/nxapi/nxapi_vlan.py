#!/usr/bin/env python3
'''
Name: nxapi_vrf.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes containing methods for retrieving vlan information

Description:
   Uses the following JSON data:

    switch# show vlan id 2000 | json-pretty 
    {
        "TABLE_vlanbriefid": {
            "ROW_vlanbriefid": {
                "vlanshowbr-vlanid": "2000", 
                "vlanshowbr-vlanid-utf": "2000", 
                "vlanshowbr-vlanname": "VLAN2000", 
                "vlanshowbr-vlanstate": "active", 
                "vlanshowbr-shutstate": "noshutdown", 
                "vlanshowplist-ifidx": "Ethernet1/53"
            }
        }, 
        "TABLE_mtuinfoid": {
            "ROW_mtuinfoid": {
                "vlanshowinfo-vlanid": "2000", 
                "vlanshowinfo-media-type": "enet", 
                "vlanshowinfo-vlanmode": "ce-vlan"
            }
        }, 
        "vlanshowrspan-vlantype": "notrspan"
    }

Synopsis:

from nxapi_netbox.nxapi.nxapi_vlan import NxapiVlanId
from nxapi_netbox.general.log import get_logger

log = get_logger('my_script_name', 'INFO', 'DEBUG')
nx = NxapiVlan('myusername','mypassword','myip', log)
# nxapi_init() can take an argparse instance to disable cookies. By default, cookies are enabled.
# see ~/lib/general/args_cookie.py for details
nx.nxapi_init()
nx.refresh()
print('id {}'.format(nx.vlan_id))
print('vlan_id_utf {}'.format(nx.vlan_id_utf))
print('name {}'.format(nx.name))
print('state {}'.format(nx.state))
print('shut_state {}'.format(nx.shut_state))
print('interfaces {}'.format(nx.interfaces))
print('media_type {}'.format(nx.media_type))
print('type {}'.format(nx.type))
print('mode {}'.format(nx.mode))

'''
our_version = 104

# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiVlanId(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self._vlan = None
        self.map_keys = dict()
        self.map_keys['vlanshowbr-vlanid'] = 'id'
        self.map_keys['vlanshowbr-vlanid-utf'] = 'id_utf'
        self.map_keys['vlanshowbr-vlanname'] = 'name'
        self.map_keys['vlanshowbr-vlanstate'] = 'state'
        self.map_keys['vlanshowbr-shutstate'] = 'shut_state'
        self.map_keys['vlanshowplist-ifidx'] = 'interfaces'
        self.map_keys['vlanshowinfo-vlanid'] = 'id'
        self.map_keys['vlanshowinfo-media-type'] = 'media_type'
        self.map_keys['vlanshowinfo-vlanmode'] = 'mode'
        self.map_keys['vlanshowrspan-vlantype'] = 'type'

    def refresh(self):
        if self.vlan == None:
            self.log.error('Exiting. Please set property instance.vlan first.  Example instance.vlan = 2')
        self.cli = 'show vlan id {}'.format(self.vlan)
        self.show()
        self.make_info_dict()

    def _populate_from_vlanbriefid(self):
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return

        _table = 'TABLE_vlanbriefid'
        _row = 'ROW_vlanbriefid'
        try:
            _dict = self.body[0][_table][_row]
        except:
            self.log.warning('{} {} early return: [{}][{}] not in self.body[0] {}'.format(self.log_prefix, self.hostname, _table, _row, self.body[0]))
            return

        _dicts = self._convert_to_list(_dict)
        for _dict in _dicts:
            if 'vlanshowbr-vlanid' not in _dict:
                self.log.debug('{} skipping. vlanshowbr-vlanid key not in _dict {}'.format(self.hostname, _dict))
                continue
            try:
                _vlan = int(_dict['vlanshowbr-vlanid'])
            except:
                self.log.error('{} Skipping. Unable to convert vlan id {} to int()'.format(_dict['vlanshowbr-vlanid']))
                continue
            for _key in _dict:
                self.log.debug('got _key {} from _dict'.format(_key))
                try:
                    self.info[self.map_keys[_key]] = _dict[_key]
                except:
                    self.log.debug('skipping unknown key {} in _dict {}'.format(_key, _dict))
                    continue

    def _populate_from_mtuinfoid(self):
        if 'TABLE_mtuinfoid' not in self.body[0]:
            self.log.debug('{} early return: no TABLE_mtuinfoid'.format(self.hostname))
            return
        if 'ROW_mtuinfoid' not in self.body[0]['TABLE_mtuinfoid']:
            self.log.debug('{} early return: no ROW_mtuinfoid'.format(self.hostname))
            return
        _dicts = self._convert_to_list(self.body[0]['TABLE_mtuinfoid']['ROW_mtuinfoid'])
        for _dict in _dicts:
            if 'vlanshowinfo-vlanid' not in _dict:
                self.log.debug('{} skipping. vlanshowinfo-vlanid key not in _vlan_dict {}'.format(self.hostname, _dict))
                continue
            try:
                _vlan = int(_dict['vlanshowinfo-vlanid'])
            except:
                self.log.error('{} Skipping. Unable to convert vlan id {} to int()'.format(_dict['vlanshowinfo-vlanid']))
                continue
            for _key in _dict:
                self.log.debug('got _key {} from _vlan_dict'.format(_key))
                try:
                    self.info[self.map_keys[_key]] = _dict[_key]
                except:
                    self.log.debug('skipping unknown key {} in _dict {}'.format(_key, _dict))
                    continue
    def _populate_vlan_show_rspan(self):
        if 'vlanshowrspan-vlantype' not in self.body[0]:
            self.log.debug('{} early return: no vlanshowrspan-vlantype'.format(self.hostname))
            return

    def make_info_dict(self):
        self.info = dict()
        self._populate_from_vlanbriefid()
        self._populate_from_mtuinfoid()
        self._populate_vlan_show_rspan()

    @property
    def interfaces(self):
        try:
            return self.info['interfaces']
        except:
            return False

    @property
    def media_type(self):
        try:
            return self.info['media_type']
        except:
            return False

    @property
    def mode(self):
        try:
            return self.info['mode']
        except:
            return False

    @property
    def name(self):
        try:
            return self.info['name']
        except:
            return False

    @property
    def shut_state(self):
        try:
            return self.info['shut_state']
        except:
            return False

    @property
    def state(self):
        try:
            return self.info['state']
        except:
            return False

    @property
    def type(self):
        try:
            return self.info['type']
        except:
            return False

    @property
    def vlan(self):
        return self._vlan
    @vlan.setter
    def vlan(self, _x):
        if not self.verify.is_digits(_x):
            self.log.error('Exiting.  vlan must be digits. Got {}.'.format(_x))
            exit(1)
        self._vlan = _x

    @property
    def vlan_id(self):
        try:
            return self.info['id']
        except:
            return False

    @property
    def vlan_id_utf(self):
        try:
            return self.info['id_utf']
        except:
            return False
