#!/usr/bin/env python3
'''
Name: nxapi_dir.py
Author: Allen Robel (arobel@cisco.com)
Summary: Classes containing methods for retrieving directory information from a NXOS switch via NXAPI

Description:

Synopsis:

#!/usr/bin/env python3
from general.log import get_logger
from nxapi.nxapi_dir import NxapiDir

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

mgmt_ip = '192.168.1.1'
log = get_logger('my_script', cfg.loglevel, 'DEBUG')
d = NxapiDir('my_username', 'my_password', mgmt_ip, log)
d.nxapi_init(cfg)
d.refresh()
print_dict(d.info, d.hostname)

'''
our_version = 105

# standard libraries
# DSSPERF libraries
from nxapi.nxapi_base import NxapiBase

class NxapiDir(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.info['files'] = dict()
        self.info['stats'] = dict()
        self._no_files = dict()
        self._no_files['refresh_not_called'] = dict()
        self._no_files['refresh_not_called']['timestring'] = 'na'
        self._no_files['refresh_not_called']['fsize'] = -1
        self._no_files['refresh_not_called']['fname'] = 'refresh_not_called'
        self.info['files'] = self._no_files
        self.info['stats']['usage'] = 'na'
        self.info['stats']['bytesused'] = -1
        self.info['stats']['bytesfree'] = -1
        self.info['stats']['bytestotal'] = -1
        self._target = None
        self.refreshed = False

    def refresh(self):
        if self.target == None:
            self.cli = 'dir'
        else:
            self.cli = 'dir {}'.format(self.target)
        self.show(self.cli)
        self.make_info_dict()

    def make_info_dict_files_key_for_legacy_systems(self, _dict):
        '''
        handle populating self.info['files'] for legacy systems, e.g. 7.0(3)I6(1)
        legacy system format was:
            "TABLE_dir": {
                "ROW_dir": {
                    "fsize": [
                        "4096", 
                        "4096"
                    ], 
                    "timestring": [
                        "Apr 11 10:39:10 2018", 
                        "Oct 18 20:51:35 2016"
                    ], 
                    "fname": [
                        ".rpmstore", 
                        "virtual-instance"
                    ]
                }
        '''
        self.log.info('got _dict {}'.format(_dict))
        if type(_dict['fsize']) != type(list()):
            self.log.error('NxapiDir.make_info_dict_files_key_for_legacy_systems: early return: expected type fsize to be list(). Got {}'.format(type(_dict['fsize'])))
            return
        if type(_dict['timestring']) != type(list()):
            self.log.error('NxapiDir.make_info_dict_files_key_for_legacy_systems: early return: expected type timestring to be list(). Got {}'.format(type(_dict['timestring'])))
            return
        if type(_dict['fname']) != type(list()):
            self.log.error('NxapiDir.make_info_dict_files_key_for_legacy_systems: early return: expected type fname to be list(). Got {}'.format(type(_dict['fname'])))
            return
        if len(_dict['fsize']) != len(_dict['timestring']):
            self.log.error('NxapiDir.make_info_dict_files_key_for_legacy_systems: early return: expected equal length lists fsize, timestring. Got {} vs {}'.format(len(_dict['fsize']), len(_dict['timestring'])))
            return
        if len(_dict['fsize']) != len(_dict['fname']):
            self.log.error('NxapiDir.make_info_dict_files_key_for_legacy_systems: early return: expected equal length lists fsize, fname. Got {} vs {}'.format(len(_dict['fsize']), len(_dict['fname'])))
            return

        for fname, timestring, fsize in zip(_dict['fname'], _dict['timestring'], _dict['fsize']):
            self.info['files'][fname] = dict()
            self.info['files'][fname]['fname'] = fname
            self.info['files'][fname]['timestring'] = timestring
            self.info['files'][fname]['fsize'] = fsize
        self.log.debug("Got self.info['files'] {}".format(self.info['files']))


    def make_info_dict(self):
        '''
        creates self.info, a two-level dict() with the following structure:
            self.info['files'][fname]['fsize']
            self.info['files'][fname]['timestring']
            self.info['files'][fname]['fname']

            self.info['stats']['usage']
            self.info['stats']['bytesused']
            self.info['stats']['bytesfree']
            self.info['stats']['bytestotal']

        Where fname is the name of each file, as returned in:
           "TABLE_dir": {"ROW_dir": [ { "fname": "<filename>" } ]

        The following JSON is referenced (from 'dir <target>' CLI)

        {
            "TABLE_dir": {
                "ROW_dir": [
                    {
                        "fsize": "1414", 
                        "timestring": "Jul 25 21:59:17 2018", 
                        "fname": "20180710_initial.cfg"
                    }, 
                    {
                        "fsize": "36416", 
                        "timestring": "Jul 27 00:56:48 2018", 
                        "fname": "base.cfg"
                    } 
                ]
            }, 
            "usage": "bootflash://sup-local", 
            "bytesused": "2541199360", 
            "bytesfree": "240068919296", 
            "bytestotal": "242610118656"
        }

        '''
        self.info = dict()
        self.info['files'] = dict()
        self.info['stats'] = dict()


        if not self._verify_body_length():
            return
        _list = self._get_table_row('dir', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if(type(_dict['fname'])) == type(list()):
                self.log.debug('{} handling legacy format'.format(self.hostname))
                self.make_info_dict_files_key_for_legacy_systems(_dict)
                break
            if 'fname' not in _dict:
                self.log.debug('{} skipping. fname key not in _file {}'.format(self.hostname,_dict['fname']))
                continue
            self.info['files'][_dict['fname']] = _dict

        for _key in self.body[0]:
            if 'TABLE' in _key:
                self.log.debug('skipping _key {} from self.body[0]'.format(_key))
                continue
            self.log.debug('adding _key {} value {} from self.body[0]'.format(_key, self.body[0][_key]))
            self.info['stats'][_key] = self.body[0][_key]


    @property
    def free(self):
        try:
            return int(str(self.info['stats']['bytesfree']))
        except:
            return -1

    @property
    def used(self):
        try:
            return int(str(self.info['stats']['bytesused']))
        except:
            return -1

    @property
    def total(self):
        try:
            return int(str(self.info['stats']['bytestotal']))
        except:
            return -1

    @property
    def files(self):
        '''
        returns a list() of dict() where each dict() is info about a file.

        Example dict()

         {'fsize': 1942212608, 'timestring': 'Apr 19 18:30:29 2022', 'fname': 'nxos64-cs.10.2.2.F.bin'}
        '''
        if 'files' not in self.info:
            return []
        return self.info['files']

    @property
    def stats(self):
        if 'stats' not in self.info:
            return []
        return self.info['stats']

    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, _x):
        self._target = _x

