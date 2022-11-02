#!/usr/bin/env python3
# NxapiBase() - nxapi_base.py
our_version = 129
'''
Name: nxapi_base.py
Author: Allen Robel (arobel@cisco.com)
Description: Base class for libraries using Nxapi 

This is not intended as a user-facing library.
Rather, its class(es) are inherited by classes in other libraries.
'''
# STANDARD libraries
import re
# local libraries
from nxapi_netbox.nxapi.nxapi_json import Nxapi
from nxapi_netbox.general.util import file2list

class NxapiBase(Nxapi):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self.lib_name = 'NxapiBase'
        self.log_prefix = '{}_{}'.format(self.lib_name, self.lib_version)
        self.contact = 'arobel@cisco.com'
        self._vrf = 'default'
        self._vrf_set_by_user = False
        self._module = 1
        self._module_set_by_user = False
        self._loglevel = 'INFO'
        self.result = dict()
        self.result_code = self.RC_200_SUCCESS
        self.SHOW_CLI_VALID = self.RC_200_SUCCESS
        self.cli = ''
        # filename containing configuration
        self._config_file = None
        # list containing configuration lines from filename self._config_file
        self._config_list = list()
        self.re_empty_line = re.compile('^\s*$')
        self.re_comment_line = re.compile('^\s*\#')

    def _convert_to_list(self, i):
        '''
        included to workaround NXOS behavior that a ROW_xxx will be a dict() if only
        a single item is in the ROW, or a list() if multiple items are in the ROW.

        Use this to convert all ROW_xxx to a list.
        '''
        if not self.verify.is_list(i):
            return [i]
        return i

    def _get_table_row(self, _name, _json):
        '''
        Given _json with below structure, and _name, return the contents of ROW as a list of dictionaries.

        "TABLE_<name>": {
            "ROW_<name>": [
                {
                    "content_key1": "content_value1", 
                    "content_key2": "content_value2"
                },
                {
                    "content_key1": "content_value1", 
                    "content_key2": "content_value2"
                },
                etc...
            ]
        }

        Example:
        self.cli = 'show forwarding ipv4 route {}'.format(self.prefix)
        self.show(self.cli)
        _list_of_dict = self._get_table_row('module', self.body[0])
        <do something with _list_of_dict>
        '''
        _table = 'TABLE_{}'.format(_name)
        _row = 'ROW_{}'.format(_name)
        try:
            _dict_list = self._convert_to_list(_json[_table][_row])
        except:
            self.log.warning('{} early return: [{}][{}] not present in _json {}'.format(self.hostname, _table, _row, _json))
            return False
        return _dict_list

    def _verify_body_length(self):
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return False
        return True

    def _get_module_dict(self):
        '''
        for cli that return JSON starting with the following, this method can be used:
        "TABLE_module": {
            "ROW_module": [
                {
                    "module_number": "1", 

        Example:
        self.cli = 'show forwarding ipv4 route {}'.format(self.prefix)
        self.show(self.cli)
        self._get_module_dict()
        <do something with above JSON>
        '''
        if self.module == None:
            self.log.error('{} early return: please set <instance>.module first.'.format(self.hostname))
            return
        if not self._verify_body_length():
            return
        self._module_dict = dict()

        _module_list = self._get_table_row('module', self.body[0])
        if _module_list == False:
            return
        for _module_dict in _module_list:
            if 'module_number' not in _module_dict:
                self.log.info('{} skipping. module_number key not in _module_dict {}'.format(self.hostname, _module_dict))
                continue
            if _module_dict['module_number'] == str(self.module):
                self._module_dict = _module_dict
                return
        self.log.warning('{} *** early return: module {} not found'.format(self.hostname, self.module))

    def configure_from_file(self):
        if self.config_file == None:
            self.log.error("{} {} exiting. set instance.config_file first.".format(self.log_prefix, self.hostname))
            exit(1)
        self.config_list = file2list(self.config_file)
        self.configure_from_list()

    def configure_from_list(self):
        if not self.verify.is_list(self.config_list):
            self.log.error("{} {} Exiting. Expected a python list. Got {}".format(self.log_prefix, self.hostname, self.config_list))
            exit(1)

        if len(self.config_list) == 0:
            self.log.warning("{} {} Early return, skipping configuration due to empty list. Check list contents".format(self.log_prefix, self.hostname))
            return

        _list = list()
        for line in self.config_list:
            m = self.re_empty_line.search(line)
            if m:
                continue
            m = self.re_comment_line.search(line)
            if m:
                continue
            _list.append(line)
        self.log.debug('{} {} sending _list {}'.format(self.log_prefix, self.hostname, _list))
        self.config_file = None
        self.config_list = _list
        self.conf()
        index = 0
        self.result_code = self.RC_200_SUCCESS
        for _code in self.conf_results:
            if _code != self.RC_200_SUCCESS:
                self.result_code = _code
                self.log.warning('{} {} Error during conf: cli {}'.format(self.log_prefix, self.hostname, self.config_list[index]))
                self.log.warning('{} {} Error during conf: result code {} -> {}'.format(self.log_prefix, self.hostname, _code, self.rc_dict[_code]))
            index += 1

    @property
    def loglevel(self):
        '''Dynamically set the logging level
           synopsis:
              c = SomeChildClass()
              c.loglevel = 'INFO'
        '''
        return self._loglevel
    @loglevel.setter
    def loglevel(self,_x):
        if not self.verify.is_loglevel(_x):
            self.loglevel.warning("{} {} {} is not a valid loglevel. Must be one of {}. loglevel not set.".format(
                             self.log_prefix,
                             self.hostname,
                             _x,
                             self.verify.valid_loglevels))
            return
        self._loglevel = _x
        self.log.setLevel(self._loglevel)

    @property
    def module(self):
        return self._module
    @module.setter
    def module(self,_x):
        if not self.verify.is_digits(_x):
            self.log.error('Exiting. module must be an integer.  Got {}'.format(_x))
            exit(1)
        self._module_set_by_user = True
        self._module = _x

    @property
    def vrf(self):
        return self._vrf
    @vrf.setter
    def vrf(self,_x):
        self._vrf_set_by_user = True
        self._vrf = _x

    @property
    def config_file(self):
        return self._config_file
    @config_file.setter
    def config_file(self, fn):
        self._config_file = fn

    @property
    def config_list(self):
        return self._config_list
    @config_list.setter
    def config_list(self, _x):
        if not self.verify.is_list(_x):
            self.log.error('{} {} Exiting. need a python list.  Got {}'.format(self.log_prefix, self.hostname, type(_x)))
            exit(1)
        self._config_list = _x
