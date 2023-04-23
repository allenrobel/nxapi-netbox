#!/usr/bin/env python3
# NxapiBase() - nxapi_base.py
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

OUR_VERSION = 130

class NxapiBase(Nxapi):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = OUR_VERSION
        self.lib_name = 'NxapiBase'
        self.log_prefix = f"{self.lib_name}_{self.lib_version}"
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
        _table = f"TABLE_{_name}"
        _row = f"ROW_{_name}"
        try:
            _dict_list = self._convert_to_list(_json[_table][_row])
        except:
            msg = f"{self.hostname} early return:"
            msg += f" [{_table}][{_row}] not present in _json {_json}"
            self.log.warning(msg)
            return False
        return _dict_list

    def _verify_body_length(self):
        if self.body_length != 1:
            msg = f"{self.hostname} early return:"
            msg += f" unexpected body_length {self.body_length}"
            self.log.error(msg)
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
            msg = f"{self.hostname} early return:"
            msg += " set <instance>.module first"
            self.log.error(msg)
            return
        if not self._verify_body_length():
            return
        self._module_dict = dict()

        _module_list = self._get_table_row("module", self.body[0])
        if _module_list == False:
            return
        for _module_dict in _module_list:
            if "module_number" not in _module_dict:
                msg = f"{self.hostname} skipping:"
                msg += f" module_number key not in _module_dict {_module_dict}"
                self.log.info(msg)
                continue
            if _module_dict["module_number"] == str(self.module):
                self._module_dict = _module_dict
                return
        msg = f"{self.hostname} early return:"
        msg += f" module {self.module} not found"
        self.log.warning(msg)


    def configure_from_file(self):
        if self.config_file == None:
            self.log.error(
                f"{self.log_prefix} {self.hostname} exiting. set instance.config_file first."
            )
            exit(1)
        self.config_list = file2list(self.config_file)
        self.configure_from_list()

    def configure_from_list(self):
        if not self.verify.is_list(self.config_list):
            msg = f"{self.log_prefix} {self.hostname} Exiting:"
            msg += f" Expected a python list. Got {self.config_list}"
            self.log.error(msg)
            exit(1)

        if len(self.config_list) == 0:
            msg = f"{self.log_prefix} {self.hostname} Early return:"
            msg += " skipping configuration due to empty config_list."
            self.log.warning(msg)
            return

        _list = []
        for line in self.config_list:
            m = self.re_empty_line.search(line)
            if m:
                continue
            m = self.re_comment_line.search(line)
            if m:
                continue
            _list.append(line)
        self.log.debug(
            f"{self.log_prefix} {self.hostname} sending _list {_list}"
        )
        self.config_file = None
        self.config_list = _list
        self.conf()
        index = 0
        self.result_code = self.RC_200_SUCCESS
        for _code in self.conf_results:
            if _code != self.RC_200_SUCCESS:
                self.result_code = _code
                msg = f"{self.log_prefix} {self.hostname} Error during conf:"
                msg += f" cli {self.config_list[index]}"
                msg += f" result code: {_code} -> {self.rc_dict[_code]}"
                self.log.warning(msg)
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
    def loglevel(self, x):
        if not self.verify.is_loglevel(x):
            msg = f"{self.log_prefix} {self.hostname} loglevel not set."
            msg += f" Reason: invalid loglevel: {x}."
            msg += f" Must be one of {self.verify.valid_loglevels}"
            self.loglevel.warning(msg)
            return
        self._loglevel = x
        self.log.setLevel(self._loglevel)

    @property
    def module(self):
        return self._module
    @module.setter
    def module(self, x):
        if not self.verify.is_digits(x):
            msg = f"{self.log_prefix} {self.hostname} Exiting."
            msg += f" Expected an integer for module.  Got {x}"
            self.log.error(msg)
            exit(1)
        self._module_set_by_user = True
        self._module = x

    @property
    def vrf(self):
        return self._vrf
    @vrf.setter
    def vrf(self, x):
        self._vrf_set_by_user = True
        self._vrf = x

    @property
    def config_file(self):
        return self._config_file
    @config_file.setter
    def config_file(self, x):
        self._config_file = x

    @property
    def config_list(self):
        return self._config_list
    @config_list.setter
    def config_list(self, x):
        if not self.verify.is_list(x):
            msg = f"{self.log_prefix} {self.hostname} Exiting."
            msg += f" Exected a python list for config_list.  Got {x}"
            self.log.error(msg)
            exit(1)
        self._config_list = x
