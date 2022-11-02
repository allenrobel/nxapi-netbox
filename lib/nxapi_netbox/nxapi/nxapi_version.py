#!/usr/bin/env python3
'''
Name: nxapi_version.py
Author: Allen Robel (arobel@cisco.com)
Description: Class to retrieve nxos version/boot information via NXAPI

NxapiVersion() corresponds to the output provided by the following cli:

show version | json-pretty

Synopsis:

our_version = 101
script_name = 'example_show_version'

from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_version import NxapiVersion

log = get_logger(script_name, 'INFO', 'DEBUG')
username = 'admin'
password = 'mypassword'
ip = '192.168.1.1'
nx = NxapiVersion(username, password, ip, log)
nx.nxapi_init()
nx.refresh()

fmt = '{:<15} {:<18} {:>9} {:<8} {:>14} {:>12} {:<13} {:<30}'
print(fmt.format(
    'ip',
    'hostname',
    'memory',
    'mem_unit',
    'bootflash_size',
    'rr_usecs',
    'bios_version',
    'nxos_version'))
print(fmt.format(
    ip,
    nx.hostname,
    nx.memory,
    nx.mem_type,
    nx.bootflash_size,
    nx.rr_usecs,
    nx.bios_ver_str,
    nx.nxos_ver_str))

Produces the following output:

% ./example_show_version.py
ip              hostname              memory mem_unit bootflash_size     rr_usecs bios_version  nxos_version                  
172.22.150.102  cvd-1311-leaf       24617848 kB             53298520       955686 07.69         10.2(3)                       
% 
'''
our_version = 103

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiVersion(NxapiBase):
    '''
    Methods for parsing the JSON below.

NX-OS Version 9.2(2)

switch# show version | json-pretty
{
    "header_str": "Cisco Nexus Operating System (NX-OS) Software\nTAC support: h
ttp://www.cisco.com/tac\nCopyright (C) 2002-2018, Cisco and/or its affiliates.\n
All rights reserved.\nThe copyrights to certain works contained in this software
 are\nowned by other third parties and used and distributed under their own\nlic
enses, such as open source.  This software is provided \"as is,\" and unless\not
herwise stated, there is no warranty, express or implied, including but not\nlim
ited to warranties of merchantability and fitness for a particular purpose.\nCer
tain components of this software are licensed under\nthe GNU General Public Lice
nse (GPL) version 2.0 or \nGNU General Public License (GPL) version 3.0  or the 
GNU\nLesser General Public License (LGPL) Version 2.1 or \nLesser General Public
 License (LGPL) Version 2.0. \nA copy of each such license is available at\nhttp
://www.opensource.org/licenses/gpl-2.0.php and\nhttp://opensource.org/licenses/g
pl-3.0.html and\nhttp://www.opensource.org/licenses/lgpl-2.1.php and\nhttp://www
.gnu.org/licenses/old-licenses/library.txt.", 
    "bios_ver_str": "07.64", 
    "kickstart_ver_str": "9.2(2) [build 9.2(1.144)]", 
    "bios_cmpl_time": "05/17/2018", 
    "kick_file_name": "bootflash:///si.921_144", 
    "kick_cmpl_time": "9/1/2018 2:00:00", 
    "kick_tmstmp": "09/01/2018 03:23:18", 
    "chassis_id": "Nexus9000 93180YC-EX chassis", 
    "cpu_name": "Intel(R) Xeon(R) CPU  @ 1.80GHz", 
    "memory": "24632668", 
    "mem_type": "kB", 
    "proc_board_id": "FD1333635DT", 
    "host_name": "switch", 
    "bootflash_size": "53298520", 
    "kern_uptm_days": "0", 
    "kern_uptm_hrs": "0", 
    "kern_uptm_mins": "48", 
    "kern_uptm_secs": "49", 
    "rr_usecs": "472225", 
    "rr_ctime": "Tue Sep  4 00:20:15 2018", 
    "rr_reason": "Reset Requested by CLI command reload", 
    "rr_sys_ver": "9.2(2)", 
    "rr_service": null, 
    "manufacturer": "Cisco Systems, Inc.", 
    "TABLE_package_list": {
        "ROW_package_list": {
            "package_id": null
        }
    }
}
switch# 

NX-OS Version 10.2(3)

{
    "header_str": "Cisco Nexus Operating System (NX-OS) Software\nTAC support: http://www.cisco.com/tac\nCopyright (C) 2002-2022, Cisco and/or its affiliates
.\nAll rights reserved.\nThe copyrights to certain works contained in this software are\nowned by other third parties and used and distributed under their ow
n\nlicenses, such as open source.  This software is provided \"as is,\" and unless\notherwise stated, there is no warranty, express or implied, including but
 not\nlimited to warranties of merchantability and fitness for a particular purpose.\nCertain components of this software are licensed under\nthe GNU General
 Public License (GPL) version 2.0 or \nGNU General Public License (GPL) version 3.0  or the GNU\nLesser General Public License (LGPL) Version 2.1 or \nLesser
 General Public License (LGPL) Version 2.0. \nA copy of each such license is available at\nhttp://www.opensource.org/licenses/gpl-2.0.php and\nhttp://opensou
rce.org/licenses/gpl-3.0.html and\nhttp://www.opensource.org/licenses/lgpl-2.1.php and\nhttp://www.gnu.org/licenses/old-licenses/library.txt.",
    "bios_ver_str": "07.69",
    "kickstart_ver_str": "10.2(3)",
    "release_type": "Feature Release",
    "nxos_ver_str": "10.2(3)",
    "bios_cmpl_time": "04/07/2021",
    "kick_file_name": "bootflash:///nxos64-cs.10.2.3.F.bin",
    "nxos_file_name": "bootflash:///nxos64-cs.10.2.3.F.bin",
    "kick_cmpl_time": "4/24/2022 3:00:00",
    "nxos_cmpl_time": "4/24/2022 3:00:00",
    "kick_tmstmp": "04/24/2022 14:54:51",
    "nxos_tmstmp": "04/24/2022 14:54:51",
    "chassis_id": "cisco Nexus9000 C93180YC-EX chassis",
    "cpu_name": "Intel(R) Xeon(R) CPU  @ 1.80GHz",
    "memory": "24617848",
    "mem_type": "kB",
    "proc_board_id": "FD13332225D",
    "host_name": "switch",
    "bootflash_size": "53298520",
    "kern_uptm_days": "1",
    "kern_uptm_hrs": "0",
    "kern_uptm_mins": "43",
    "kern_uptm_secs": "43",
    "rr_usecs": "955686",
    "rr_ctime": "Mon Oct 17 23:45:55 2022",
    "rr_reason": "Reset Requested by CLI command reload",
    "rr_sys_ver": "10.2(3)",
    "rr_service": null,
    "plugins": "Core Plugin, Ethernet Plugin",
    "manufacturer": "Cisco Systems, Inc.",
    "TABLE_package_list": {
        "ROW_package_list": {
            "package_id": null
        }
    }
}

    Resulting dictionary structure is identical to the above, except the following:
       1. "TABLE_package_list": {"ROW_package_list": {"package_id": null}}
    Is reduced to a list of dict():
        [ {'package_list': {'package_id': value}},{'package_list': {'package_id': value}},{'package_list': {'package_id': value}},etc... ]

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info_dict = dict()
        self._local_disc = -1

    def make_info_dict(self):
        '''
        from self.body[0] populate self._info_dict dict(),
        dict() structure is identical to returned JSON except for package_list/
        '''
        self._info_dict = dict()
        try:
            _dict = self.body[0]
        except:
            self.log.debug('{} early return: unable to find dict() in self.body {}'.format(self.hostname, self.body))
            return

        for key in _dict:
            if key == 'TABLE_package_list':
                _package_list = self._convert_to_list(_dict[key])
                self._info_dict['package_list'] = _package_list
                continue
            self._info_dict[key] = _dict[key]

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for key in self._info_dict:
            self.log.info('{} self._info_dict[{}] = {}'.format(self.hostname, key, self._info_dict[key]))

    def refresh(self):
        self.cli = 'show version'
        self.show(self.cli)
        self.make_info_dict()
 
    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info_dict
        except:
            return dict()

    @property
    def bios_cmpl_time(self):
        try:
            return self._info_dict['bios_cmpl_time']
        except:
            return 'na'

    @property
    def bios_ver_str(self):
        try:
            return self._info_dict['bios_ver_str']
        except:
            return 'na'

    @property
    def bootflash_size(self):
        try:
            return self._info_dict['bootflash_size']
        except:
            return 'na'

    @property
    def chassis_id(self):
        try:
            return self._info_dict['chassis_id']
        except:
            return 'na'

    @property
    def cpu_name(self):
        try:
            return self._info_dict['cpu_name']
        except:
            return 'na'

    @property
    def header_str(self):
        try:
            return self._info_dict['header_str']
        except:
            return 'na'

    @property
    def host_name(self):
        try:
            return self._info_dict['host_name']
        except:
            return 'na'

    @property
    def kickstart_ver_str(self):
        try:
            return self._info_dict['kickstart_ver_str']
        except:
            return 'na'

    @property
    def kick_file_name(self):
        try:
            return self._info_dict['kick_file_name']
        except:
            return 'na'

    @property
    def kick_cmpl_time(self):
        try:
            return self._info_dict['kick_cmpl_time']
        except:
            return 'na'

    @property
    def kick_tmstmp(self):
        try:
            return self._info_dict['kick_tmstmp']
        except:
            return 'na'

    @property
    def memory(self):
        try:
            return self._info_dict['memory']
        except:
            return 'na'

    @property
    def mem_type(self):
        try:
            return self._info_dict['mem_type']
        except:
            return 'na'

    @property
    def plugins(self):
        try:
            return self._info_dict['plugins']
        except:
            return 'na'

    @property
    def proc_board_id(self):
        try:
            return self._info_dict['proc_board_id']
        except:
            return 'na'

    @property
    def kern_uptm_days(self):
        try:
            return self._info_dict['kern_uptm_days']
        except:
            return 'na'

    @property
    def kern_uptm_hrs(self):
        try:
            return self._info_dict['kern_uptm_hrs']
        except:
            return 'na'

    @property
    def kern_uptm_mins(self):
        try:
            return self._info_dict['kern_uptm_mins']
        except:
            return 'na'

    @property
    def kern_uptm_secs(self):
        try:
            return self._info_dict['kern_uptm_secs']
        except:
            return 'na'

    @property
    def manufacturer(self):
        try:
            return self._info_dict['manufacturer']
        except:
            return 'na'

    @property
    def nxos_cmpl_time(self):
        try:
            return self._info_dict['nxos_cmpl_time']
        except:
            return 'na'

    @property
    def nxos_file_name(self):
        try:
            return self._info_dict['nxos_file_name']
        except:
            return 'na'

    @property
    def nxos_tmstmp(self):
        try:
            return self._info_dict['nxos_tmstmp']
        except:
            return 'na'

    @property
    def nxos_ver_str(self):
        try:
            return self._info_dict['nxos_ver_str']
        except:
            return 'na'

    @property
    def package_list(self):
        try:
            return self._info_dict['package_list']
        except:
            return 'na'

    @property
    def rr_usecs(self):
        try:
            return self._info_dict['rr_usecs']
        except:
            return 'na'

    @property
    def rr_ctime(self):
        try:
            return self._info_dict['rr_ctime']
        except:
            return 'na'

    @property
    def rr_reason(self):
        try:
            return self._info_dict['rr_reason']
        except:
            return 'na'

    @property
    def rr_service(self):
        try:
            return self._info_dict['rr_service']
        except:
            return 'na'

    @property
    def rr_sys_ver(self):
        try:
            return self._info_dict['rr_sys_ver']
        except:
            return 'na'



