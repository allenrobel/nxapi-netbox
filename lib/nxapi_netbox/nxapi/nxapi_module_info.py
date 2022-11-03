#!/usr/bin/env python3
'''
Name: nxapi_ip_route_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving module (linecard) status from NXOS device via NXAPI

This corresponds to the output below:

switch# sh module | json-pretty 
{
    "TABLE_modinfo": {
        "ROW_modinfo": {
            "modinf": "1", 
            "ports": "54", 
            "modtype": "48x10/25G + 6x40/100G Ethernet Module", 
            "model": "N9K-C93180YC-EX", 
            "status": "active *"
        }
    }, 
    "TABLE_modwwninfo": {
        "ROW_modwwninfo": {
            "modwwn": "1", 
            "sw": "7.0(3)I7(3)", 
            "hw": "1.0", 
            "slottype": "NA"
        }
    }, 
    "TABLE_modmacinfo": {
        "ROW_modmacinfo": {
            "modmac": "1", 
            "mac": "00-6b-f1-83-cf-00 to 00-6b-f1-83-cf-4f", 
            "serialnum": "FDO20380BKL"
        }
    }, 
    "TABLE_moddiaginfo": {
        "ROW_moddiaginfo": {
            "mod": "1", 
            "diagstatus": "Pass"
        }
    }
}
switch# 

'''
our_version = 106

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiModuleInfo(NxapiBase):
    '''
    Methods for parsing the JSON below.

    Creates the following dictionaries, all keyed on module number

    self.modinfo[module]['modinf'] = <module number>
    self.modinfo[module]['ports'] = <number of ports>
    self.modinfo[module]['modtype'] = <module type string>
    self.modinfo[module]['model'] = <model string>
    self.modinfo[module]['status'] = <module state>

    self.modwwninfo[module]['modwwn'] = <module number>
    self.modwwninfo[module]['sw'] = <software version>
    self.modwwninfo[module]['hw'] = <hardware version>
    self.modwwninfo[module]['slottype'] = <type of slot>

    self.modmacinfo[module]['modmac'] = <module number>
    self.modmacinfo[module]['mac'] = <mac address range>
    self.modmacinfo[module]['serialnum'] = <serial number>

    self.moddiaginfo[module]['mod'] = <module number>
    self.moddiaginfo[module]['diagstatus'] = <diagnostic status>

    From the following JSON returned by 'show module':

    {
        "TABLE_modinfo": {
            "ROW_modinfo": {
                "modinf": "1", 
                "ports": "54", 
                "modtype": "48x10/25G + 6x40/100G Ethernet Module", 
                "model": "N9K-C93180YC-EX", 
                "status": "active *"
            }
        }, 
        "TABLE_modwwninfo": {
            "ROW_modwwninfo": {
                "modwwn": "1", 
                "sw": "7.0(3)I7(3)", 
                "hw": "1.0", 
                "slottype": "NA"
            }
        }, 
        "TABLE_modmacinfo": {
            "ROW_modmacinfo": {
                "modmac": "1", 
                "mac": "00-6b-f1-83-cf-00 to 00-6b-f1-83-cf-4f", 
                "serialnum": "FDO20380BKL"
            }
        }, 
        "TABLE_moddiaginfo": {
            "ROW_moddiaginfo": {
                "mod": "1", 
                "diagstatus": "Pass"
            }
        }
    }
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.modinfo = dict()
        self.modwwninfo = dict()
        self.modmacinfo = dict()
        self.moddiaginfo = dict()
        self._module = -1
        # used in method module_info() to ensure the user has called self.refresh()
        # set to True in self.refresh()
        self.refreshed = False
        # why the module number item in each object has to be uniquely-named is beyond me.
        # but, it is what it is
        # the dict() below ensures we use the correct key to access the module number for
        # each of the objects returned by 'show module'
        self.module_key_dict = dict()
        self.module_key_dict['TABLE_modinfo'] = 'modinf'
        self.module_key_dict['TABLE_modwwninfo'] = 'modwwn'
        self.module_key_dict['TABLE_modmacinfo'] = 'modmac'
        self.module_key_dict['TABLE_moddiaginfo'] = 'mod'

    def _module_to_int(self, _module):
        try:
            __module = int(_module)
        except:
            self.log.error('returning __module = 1: unable to convert _module {} to integer.'.format(_module))
        return __module

    def __make_dict(self):
        _dict = dict()
        try:
            _mod_dict = self.body[0][self.table][self.row]
        except:
            self.log.warning('{} Skipping. Unable to find [{}][{}] in {}'.format(self.hostname, self.table, self.row, self.body[0]))
            return False
        _mod_info = self._convert_to_list(_mod_dict)
        for item in _mod_info:
            self.log.debug('got item {}'.format(item))
            _module = self._module_to_int(item[self.module_key_dict[self.table]])
            if _module == -1:
                self.log.error('skipping: module_to_int returned -1 for item {}'.format(item))
                continue
            _dict[_module] = dict()
            for key in item:
                self.log.debug('got key {} value'.format(key, item[key]))
                _dict[_module][key] = item[key]
        return _dict

    def make_modinfo(self):
        '''
        "TABLE_modinfo": {
            "ROW_modinfo": {
                "modinf": "1", 
                "ports": "54", 
                "modtype": "48x10/25G + 6x40/100G Ethernet Module", 
                "model": "N9K-C93180YC-EX", 
                "status": "active *"
            }
        '''
        self.table = 'TABLE_modinfo'
        self.row = 'ROW_modinfo'
        self.module_key = self.module_key_dict[self.table]
        self.modinfo = self.__make_dict()

    def make_modwwninfo(self):
        '''
        "TABLE_modwwninfo": {
            "ROW_modwwninfo": {
                "modwwn": "1", 
                "sw": "7.0(3)I7(3)", 
                "hw": "1.0", 
                "slottype": "NA"
            }
        '''
        self.table = 'TABLE_modwwninfo'
        self.row = 'ROW_modwwninfo'
        self.module_key = self.module_key_dict[self.table]
        self.modwwninfo = self.__make_dict()

    def make_modmacinfo(self):
        '''
        "TABLE_modmacinfo": {
            "ROW_modmacinfo": {
                "modmac": "1", 
                "mac": "00-6b-f1-83-cf-00 to 00-6b-f1-83-cf-4f", 
                "serialnum": "FDO20380BKL"
            }
        '''
        self.table = 'TABLE_modmacinfo'
        self.row = 'ROW_modmacinfo'
        self.module_key = self.module_key_dict[self.table]
        self.modmacinfo = self.__make_dict()

    def make_moddiaginfo(self):
        '''
        "TABLE_moddiaginfo": {
            "ROW_moddiaginfo": {
                "mod": "1", 
                "diagstatus": "Pass"
            }
        }
        '''
        self.table = 'TABLE_moddiaginfo'
        self.row = 'ROW_moddiaginfo'
        self.module_key = self.module_key_dict[self.table]
        self.moddiaginfo = self.__make_dict()

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for _key in self.modinfo:
            self.log.debug('{} self.modinfo[{}] = {}'.format(self.hostname, _key, self.modinfo[_key]))
        for _key in self.modwwninfo:
            self.log.debug('{} self.modwwninfo[{}] = {}'.format(self.hostname, _key, self.modwwninfo[_key]))
        for _key in self.modmacinfo:
            self.log.debug('{} self.modmacinfo[{}] = {}'.format(self.hostname, _key, self.modmacinfo[_key]))
        for _key in self.moddiaginfo:
            self.log.debug('{} self.moddiaginfo[{}] = {}'.format(self.hostname, _key, self.moddiaginfo[_key]))

    def refresh(self):
        self.refreshed = True
        self.cli = 'show module'
        self.show(self.cli)
        self.make_modinfo()
        self.make_modwwninfo()
        self.make_modmacinfo()
        self.make_moddiaginfo()
        self.print_dicts()
        self.refreshed = True

    def module_info(self):
        '''
        returns a dict() which filters self.module from the main dictionaries.
        The returned dict() keys are the same as the names of the main dictionaries i.e.:
            modifno
            modwwninfo
            modmacinfo
            moddiaginfo
        If self.module is not found in the main dict() associated with each of the above keys, an
        empty dict() is returned for that key
        '''
        return_dict = dict()
        if self.module not in self.modinfo:
            self.log.debug('module {} not found in modinfo. Returning empty dict() for modinfo'.format(self.module))
            return_dict['modinfo'] = dict()
        else:
            return_dict['modinfo'] = self.modinfo[self.module]

        if self.module not in self.modwwninfo:
            self.log.debug('module {} not found in modwwninfo. Returning empty dict() for modwwninfo'.format(self.module))
            return_dict['modwwninfo'] = dict()
        else:
            return_dict['modwwninfo'] = self.modwwninfo[self.module]

        if self.module not in self.modmacinfo:
            self.log.debug('module {} not found in modmacinfo. Returning empty dict() for modmacinfo'.format(self.module))
            return_dict['modmacinfo'] = dict()
        else:
            return_dict['modmacinfo'] = self.modmacinfo[self.module]

        if self.module not in self.moddiaginfo:
            self.log.debug('module {} not found in moddiaginfo. Returning empty dict() for moddiaginfo'.format(self.module))
            return_dict['moddiaginfo'] = dict()
        else:
            return_dict['moddiaginfo'] = self.moddiaginfo[self.module]

        self.log.debug('returning {}'.format(return_dict))
        return return_dict

    def refresh_needed(self):
        self.log.error('exiting. call instance.refresh() before trying to access properties.')
        exit(1)

    def verify_module_dict(self, d, key):
        if self.module not in d:
            self.log.error('exiting. module {} not in ')


    @property
    def module(self):
        return self._module
    @module.setter
    def module(self,_x):
        self._module = _x

    # moddiaginfo
    @property
    def diagstatus(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.moddiaginfo[self.module]['diagstatus']

    @property
    def mod(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.moddiaginfo[self.module]['mod']

    # modmacinfo
    @property
    def mac(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modmacinfo[self.module]['mac']

    @property
    def serialnum(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modmacinfo[self.module]['serialnum']

    @property
    def modmac(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modmacinfo[self.module]['modmac']

    # modinfo
    @property
    def model(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modinfo[self.module]['model']

    @property
    def modinf(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modinfo[self.module]['modinf']

    @property
    def modtype(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modinfo[self.module]['modtype']

    @property
    def ports(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modinfo[self.module]['ports']

    @property
    def status(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modinfo[self.module]['status']

    # modwwninfo
    @property
    def hw(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modwwninfo[self.module]['hw']

    @property
    def modwwn(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modwwninfo[self.module]['modwwn']

    @property
    def slottype(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modwwninfo[self.module]['slottype']

    @property
    def sw(self):
        if self.refreshed == False:
            self.refresh_needed()
        return self.modwwninfo[self.module]['sw']

