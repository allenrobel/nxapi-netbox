#!/usr/bin/env python3
'''
Name: nxapi_ipv6_neighbor_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving ipv6 neighbor information 

NxapiIpv6NeighborSummary() corresponds to the output provided by the following cli:

show ipv6 neighbor summary

switch# sh ipv6 neighbor summary | json-pretty
{
    "count-static": "0", 
    "count-dynamic": "42", 
    "count-others": "0", 
    "count-throttle": "0", 
    "count-total": "42"
}
switch# 


Example usage:

#!/usr/bin/env python
from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_ipv6_neighbor_summary import NxapiIpv6NeighborSummary
def print_header():
    print(fmt.format(
        'hostname',
        'vrf',
        'static',
        'dynamic',
        'others',
        'throttle',
        'total'))
# INFO logging to screen, DEBUG logging to file /tmp/script_name.log
log = get_logger('script_name', 'INFO', 'DEBUG')
nx = NxapiIpv6NeighborSummary('myusername', 'mypassword', '192.168.11.102', log)
nx.nxapi_init()
nx.vrf = 'default'
nx.refresh()
fmt = '{:<20} {:<10} {:<13} {:<15} {:<15} {:<12} {:<12}'
print_header()
print(fmt.format(
    nx.hostname,
    nx.vrf,
    nx.static,
    nx.dynamic,
    nx.others,
    nx.throttle,
    nx.total))

Output would be similar to:

% ./example_ipv6_neighbor_summary.py   
hostname             vrf        static        dynamic         others          throttle     total       
cvd-1311-leaf        default    0             1               0               0            1           
% 

'''
our_version = 101

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiIpv6NeighborSummary(NxapiBase):
    '''
    Methods for parsing the JSON below.

    oz-201v6# sh ipv6 neighbor summary | json-pretty
    {
        "count-static": "0", 
        "count-dynamic": "42", 
        "count-others": "0", 
        "count-throttle": "0", 
        "count-total": "42"
    }
    oz-201v6# 

    Creates a dictionary, self.info, with the following structure:

    self.info['static'] = int()
    self.info['dynamic'] = int()
    self.info['others'] = int()
    self.info['throttle'] = int()
    self.info['total'] = int()

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch
    self.vrf - the vrf in which arps were queried (defaults to vrf 'default')

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self._vrf = 'default'

    def _get_vrf_dict(self):
        '''
        NOT CURRENTLY USED
        Keeping in case 'show ipv6 neighbor summary' is ever changed to return TABLE_vrf/ROW_vrf like 'show ip arp summary'

        sets self._vrf_dict

        self._vrf_dict will contain the information associated with self.vrf
        if expected keys are not present, self._vrf_dict will be empty
        {
            "TABLE_vrf": {
                "ROW_vrf": {   <<<<<<<<<<<<<<<<<<<
                    "vrf-name-out": "default", 
                    "cnt-resolved": "6", 
                    "cnt-incomplete": "0", 
                    "cnt-thrtld-incomplete": "0", 
                    "cnt-unknown": "0", 
                    "cnt-total": "6"
                }
            }
        }
        '''
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        self._vrf_dict = dict()
        try:
            _vrf_list = self._convert_to_list(self.body[0]['TABLE_vrf']['ROW_vrf'])
        except:
            self.log.debug('{} early return due to keys [TABLE_vrf][ROW_vrf] not present in self.body[0] {}'.format(self.hostname, self.body[0]))
            return
        for _vrf_dict in _vrf_list:
            if 'vrf-name-out' not in _vrf_dict:
                continue
            if _vrf_dict['vrf-name-out'] != self.vrf:
                continue
            self._vrf_dict = _vrf_dict


    def make_info_dict(self):
        '''
        from self.body[0] populate self.info dict(),
        dict() structure is:
            self.info['static'] = int()
            self.info['dynamic'] = int()
            self.info['others'] = int()
            self.info['throttle'] = int()
            self.info['total'] = int()
        '''
        self.info = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return

        _expected_keys = ['count-static', 'count-dynamic', 'count-others', 'count-throttle', 'count-total']
        for key in _expected_keys:
            if key not in self.body[0]:
                self.log.debug('{} Returning empty self.info dict() due to key {} not found in self.body[0] {}'.format(
                    self.hostname,
                    key,
                    self.body[0]))
                return
        self.info['static'] = self.body[0]['count-static']
        self.info['dynamic'] = self.body[0]['count-dynamic']
        self.info['others'] = self.body[0]['count-others']
        self.info['throttle'] = self.body[0]['count-throttle']
        self.info['total'] = self.body[0]['count-total']

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for key in self.info:
            self.log.info('{} self.info[{}] = {}'.format(self.hostname, key, self.info[key]))

    def refresh(self):
        self.cli = 'show ipv6 neighbor summary vrf {}'.format(self.vrf)
        self.show(self.cli)
        self.make_info_dict()

    @property
    def static(self):
        try:
            return self.info['static']
        except:
            return -1

    @property
    def dynamic(self):
        try:
            return self.info['dynamic']
        except:
            return -1

    @property
    def others(self):
        try:
            return self.info['others']
        except:
            return -1

    @property
    def throttle(self):
        try:
            return self.info['throttle']
        except:
            return -1

    @property
    def total(self):
        try:
            return self.info['total']
        except:
            return -1

