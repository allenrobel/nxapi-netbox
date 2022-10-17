#!/usr/bin/env python3
'''
Name: nxapi_lldp.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving lldp information via NXAPI

NxapiLldpNeighbors() corresponds to the output provided by the following cli:

show lldp neighbors

Synopsis:

from general.log import get_logger
from nxapi.nxapi_lldp import NxapiLldpNeighbors

lldp = NxapiLldpNeighbors('admin', 'mypassword', '192.168.1.1', log)
lldp.nxapi_init(cfg)
lldp.refresh()
fmt = '{:<10} {:<10} {:<10} {:<13} {:<15}'
print(fmt.format('local_name', 'local_port', 'nbr_name', 'nbr_port', 'nbr_mgmt_ip'))
for local_port in lldp.lldp_neighbors:
    print(fmt.format(
        lldp.hostname,
        local_port,
        lldp.lldp_neighbors[local_port]['chassis_id'],
        lldp.lldp_neighbors[local_port]['port_id'],
        lldp.lldp_neighbors[local_port]['mgmt_addr']))


Would produce the following output:

$ ./nxapi_lldp_neighbors_example.py 
local_name local_port nbr_name   nbr_port      nbr_mgmt_ip    
bb_306     Eth1/1     bb_203     Ethernet1/3   172.22.133.193 
bb_306     Eth1/2     bb_203     Ethernet1/4   172.22.133.193 
bb_306     Eth1/3     bb_204     Ethernet1/3   172.22.133.194 
bb_306     Eth1/4     bb_204     Ethernet1/4   172.22.133.194 
'''
our_version = 104

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiLldpNeighbors(NxapiBase):
    '''
    Methods for parsing the JSON below.

{
    "neigh_hdr": "neigh_hdr", 
    "TABLE_nbor": {
        "ROW_nbor": [
            {
                "chassis_type": "7",
                "chassis_id": "bb_203",
                "l_port_id": "Eth1/1",
                "ttl": "120",
                "system_capability": "BR",
                "enabled_capability": "BR",
                "port_type": "5",
                "port_id": "Ethernet1/3",
                "mgmt_addr_type": "IPV4",
                "mgmt_addr": "192.168.1.1",
                "mgmt_addr_ipv6_type": "802",
                "mgmt_addr_ipv6": "380e.4d6e.9660"
            }, 
            etc...

    Creates the following dictionaries, all keyed on l_port_id e.g. 'Eth1/1'

    self.info[l_port_id]['chassis_type']
    self.info[l_port_id]['chassis_id']
    self.info[l_port_id]['l_port_id']
    self.info[l_port_id]['ttl']
    self.info[l_port_id]['system_capability']
    self.info[l_port_id]['enabled_capability']
    self.info[l_port_id]['port_type']
    self.info[l_port_id]['port_id']
    self.info[l_port_id]['mgmt_addr_type']
    self.info[l_port_id]['mgmt_addr']
    self.info[l_port_id]['mgmt_addr_ipv6_type']
    self.info[l_port_id]['mgmt_addr_ipv6']

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()

    def make_info_dict(self):
        '''
        from self.body populate self.info dict(), keyed on l_port_id,
        dict() structure is:
            self.info[l_port_id]['chassis_type']
            self.info[l_port_id]['chassis_id']
            self.info[l_port_id]['l_port_id']
            self.info[l_port_id]['ttl']
            self.info[l_port_id]['system_capability']
            self.info[l_port_id]['enabled_capability']
            self.info[l_port_id]['port_type']
            self.info[l_port_id]['port_id']
            self.info[l_port_id]['mgmt_addr_type']
            self.info[l_port_id]['mgmt_addr']
            self.info[l_port_id]['mgmt_addr_ipv6_type']
            self.info[l_port_id]['mgmt_addr_ipv6']
        '''
        self.info = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        try:
            _dict_path = self.body[0]['TABLE_nbor']['ROW_nbor']
        except:
            self.log.error('{} early return: unable to find appropriate path in {}'.format(self.hostname, self.body[0]))
            return

        for _dict in _dict_path:
            if 'l_port_id' not in _dict:
                continue
            nbr_key = _dict['l_port_id']
            self.info[nbr_key] = dict()
            for key in _dict:
                self.info[nbr_key][key] = _dict[key]

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for local_port in self.info:
            for key in self.info[local_port]:
                self.log.info('{} self.info[{}][{}] = {}'.format(self.hostname, local_port, key, self.info[local_port][key]))

    def refresh(self):
        self.cli = 'show lldp neighbors'
        self.show(self.cli)
        self.make_info_dict()
 
