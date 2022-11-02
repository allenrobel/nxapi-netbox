#!/usr/bin/env python3
'''
Name: nxapi_bfd.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving bfd information 

NxapiBfdNeighbors() corresponds to the output provided by the following cli:

show bfd neighbors detail

Synopsis:

from nxapi_netbox.general.log import get_logger
from nxapi_netbox.nxapi.nxapi_bfd import NxapiBfdNeighbors
mgmt_ip = '172.22.159.4'
log = get_logger('my_script', 'INFO', 'DEBUG')
bfd = NxapiBfdNeighbors('admin', 'password', mgmt_ip, log)

# optionally
# bfd.ipv6 = True
bfd.refresh()
fmt = '{:<10} {:<10} {:<13} {:<15} {:<15} {:<12} {:<12}
print(fmt.format(
    'hostname',
    'local_disc',
    'intf',
    'src_ip_addr',
    'dest_ip_addr',
    'local_state',
    'remote_state'))

print('individual @property access example')

for local_disc in bfd.info:
    bfd.local_disc = local_disc
    print(fmt.format(
        bfd.hostname,
        bfd.local_disc,
        bfd.intf,
        bfd.src_ip_addr,
        bfd.dest_ip_addr,
        bfd.local_state,
        bfd.remote_state))

print('dictionary access example')

for local_disc in bfd.info:
    print(fmt.format(
        bfd.hostname,
        bfd.info[local_disc]['local_disc'],
        bfd.info[local_disc]['intf'],
        bfd.info[local_disc]['src_ip_addr'],
        bfd.info[local_disc]['dest_ip_addr'],
        bfd.info[local_disc]['local_state'],
        bfd.info[local_disc]['remote_state']))


Would produce the following output:

$ ./bfd_test.py 
dut        local_disc intf          src_ip_addr     dest_ip_addr    local_state  remote_state
individual @property access example
ts_104     1090519041 Ethernet1/49  10.135.14.2     10.135.14.1     Up           Up          
ts_104     1090519042 Ethernet1/50  10.136.14.2     10.136.14.1     Up           Up          
dictionary access example
ts_104     1090519041 Ethernet1/49  10.135.14.2     10.135.14.1     Up           Up          
ts_104     1090519042 Ethernet1/50  10.136.14.2     10.136.14.1     Up           Up          
$ 

'''
our_version = 111

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiBfdNeighbors(NxapiBase):
    '''
    Methods for parsing the JSON below.

    ts_104# sh bfd neighbors application bgp detail | json-pretty 
    {
        "TABLE_bfdNeighbor": {
            "ROW_bfdNeighbor": [
                {
                    "local_disc": "1090519041", 
                    "header": "1", 
                    "vrf_name": "default", 
                    "src_ip_addr": "10.135.14.2", 
                    "src_ipv6_addr": "0::", 
                    "dest_ip_addr": "10.135.14.1", 
                    "dest_ipv6_addr": "0::", 
                    "remote_disc": "1090519041", 
                    "local_state": "Up", 
                    "remote_state": "Up", 
                    "holddown": "6872", 
                    "cur_detect_mult": "4", 
                    "intf": "Ethernet1/49", 
                    "out_str": null, 
                    "echo": "1", 
                    "echo_tx": "50000", 
                    "local_diag": "0", 
                    "demand": "0", 
                    "poll": "0", 
                    "min_tx": "50000", 
                    "min_rx": "2000000", 
                    "local_multi": "4", 
                    "dectect_timer": "8000000", 
                    "down_count": "0", 
                    "tx_interval": "2000000", 
                    "rx_count": "3038", 
                    "rx_avg": "1690", 
                    "rx_min": "160", 
                    "rx_max": "1923", 
                    "last_rx": "1127", 
                    "tx_count": "2944", 
                    "tx_avg": "1743", 
                    "tx_min": "1743", 
                    "tx_max": "1743", 
                    "last_tx": "1020", 
                    "app": "bgp", 
                    "up_time": "5128000", 
                    "version": "1", 
                    "diag": "0", 
                    "state_bit": "Up", 
                    "demand_bit": "0", 
                    "poll_bit": "0", 
                    "final_bit": "0", 
                    "multiplier": "4", 
                    "length": "24", 
                    "my_disc": "1090519041", 
                    "your_disc": "1090519041", 
                    "min_tx_interval": "50000", 
                    "req_min_rx": "2000000", 
                    "min_echo_interval": "50000", 
                    "host_lc": "1", 
                    "down_reason": "None", 
                    "no_host_reason": "None", 
                    "parent": "0", 
                    "per_link_str": null, 
                    "auth": "None", 
                    "auth_bit": "0", 
                    "print_details": "1"
                }, 

    Creates a 2-level dictionary, keyed on local_disc e.g. '1090519041'
    whose second-level keys are the same as the JSON above e.g.
    self._info_dict[local_disc]['local_disc'] = "1090519041"
    self._info_dict[local_disc]['header'] = "1"
    self._info_dict[local_disc]['vrf_name'] = "default"
    self._info_dict[local_disc]['local_state'] = "Up"
    self._info_dict[local_disc]['remote_state'] = "Up"
    self._info_dict[local_disc]['down_reason'] = "Up"
    self._info_dict[local_disc]['app'] = "bgp"

    The following var is also set:
    self.hostname -  will equal the value of the hostname configuration on the target switch

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._info_dict = dict()
        self._local_disc = -1
        # see property @ipv6
        # determines which cli to use.
        # if self.ipv6 is False, use 'show bfd ipv4 neighbor detail'
        # if self.ipv6 is True, use 'show bfd ipv6 neighbor detail' 
        self._ipv6 = False


    def make_info_dict(self):
        '''
        from self.body populate self._info_dict dict(), keyed on local_disc,
        dict() structure is:
            self._info_dict[local_disc]['local_disc'] = "1090519041"
            self._info_dict[local_disc]['header'] = "1"
            self._info_dict[local_disc]['vrf_name'] = "default"
            etc, for all keys in the JSON found in the main class docstring
        '''
        self._info_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('bfdNeighbor', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            try:
                _local_disc = int(_dict['local_disc'])
            except:
                self.log.error('{} early return: unable to find [local_disc], or [local_disc] not convertable to int() _dict {}'.format(self.hostname, _dict))
                return
            self._info_dict[_local_disc] = _dict

    def print_dicts(self):
        '''
        print the contents of all dictionaries
        '''
        for local_disc in self._info_dict:
            for key in self._info_dict[local_disc]:
                self.log.info('{} self._info_dict[{}][{}] = {}'.format(self.hostname, local_disc, key, self._info_dict[local_disc][key]))

    def refresh(self):
        if self.ipv6 == False:
            self.cli = 'show bfd ipv4 neighbors detail'
        elif self.ipv6 == True:
            self.cli = 'show bfd ipv6 neighbors detail'
        else:
            self.log.error('Exiting. Unknown value for self.ipv6: {}'.format(self.ipv6))
            exit(1)
        # REVERT
        #self.show()
        self.show(self.cli)
        self.make_info_dict()
 
    @property
    def ipv6(self):
        return self._ipv6
    @ipv6.setter
    def ipv6(self,_x):
        if type(_x) != type(False):
            self.log.error("Exiting. Expected boolean. Got {}".format(_x))
            exit(1)
        self._ipv6 = _x


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
    def info_disc(self):
        '''
        return the portion of self._info_dict whose key is self.local_disc
        '''
        try:
            return self._info_dict[self.local_disc]
        except:
            return dict()

    @property
    def local_disc(self):
        return self._local_disc
    @local_disc.setter
    def local_disc(self, _x):
        '''
        if self.local_disc is set, then properties to retrieve items from within self._info_dict will return 
        items associated with self.local_dict
        '''
        if not self.verify.is_int(_x):
            self.log.debug('ignored. expected integer')
            return
        self._local_disc = _x

    @property
    def app(self):
        try:
            return self._info_dict[self.local_disc]['app']
        except:
            return 'na'

    @property
    def auth(self):
        try:
            return self._info_dict[self.local_disc]['auth']
        except:
            return 'na'

    @property
    def auth_bit(self):
        try:
            return self._info_dict[self.local_disc]['auth_bit']
        except:
            return 'na'

    @property
    def cur_detect_mult(self):
        try:
            return self._info_dict[self.local_disc]['cur_detect_mult']
        except:
            return 'na'

    @property
    def detect_timer(self):
        try:
            # Earlier images had a typo for the detect_timer key, support
            # these images too...
            if 'dectect_timer' in self._info_dict[self.local_disc]:
                return self._info_dict[self.local_disc]['dectect_timer']
            else:
                return self._info_dict[self.local_disc]['detect_timer']
        except:
            return 'na'

    @property
    def demand(self):
        try:
            return int(self._info_dict[self.local_disc]['demand'])
        except:
            return 'na'

    @property
    def demand_bit(self):
        try:
            return int(self._info_dict[self.local_disc]['demand_bit'])
        except:
            return -1

    @property
    def dest_ip_addr(self):
        try:
            return self._info_dict[self.local_disc]['dest_ip_addr']
        except:
            return 'na'

    @property
    def dest_ipv6_addr(self):
        try:
            return self._info_dict[self.local_disc]['dest_ipv6_addr']
        except:
            return 'na'

    @property
    def diag(self):
        try:
            return self._info_dict[self.local_disc]['diag']
        except:
            return 'na'

    @property
    def down_count(self):
        try:
            return int(self._info_dict[self.local_disc]['down_count'])
        except:
            return -1

    @property
    def down_reason(self):
        try:
            return self._info_dict[self.local_disc]['down_reason']
        except:
            return 'na'

    @property
    def echo(self):
        try:
            return self._info_dict[self.local_disc]['echo']
        except:
            return -1


    @property
    def echo_tx(self):
        try:
            return int(self._info_dict[self.local_disc]['echo_tx'])
        except:
            return -1

    @property
    def final_bit(self):
        try:
            return int(self._info_dict[self.local_disc]['final_bit'])
        except:
            return -1

    @property
    def header(self):
        try:
            return self._info_dict[self.local_disc]['header']
        except:
            return 'na'

    @property
    def holddown(self):
        try:
            return int(self._info_dict[self.local_disc]['holddown'])
        except:
            return -1

    @property
    def host_lc(self):
        try:
            return int(self._info_dict[self.local_disc]['host_lc'])
        except:
            return -1

    @property
    def intf(self):
        try:
            return self._info_dict[self.local_disc]['intf']
        except:
            return 'na'

    @property
    def last_rx(self):
        try:
            return int(self._info_dict[self.local_disc]['last_rx'])
        except:
            return -1

    @property
    def last_tx(self):
        try:
            return int(self._info_dict[self.local_disc]['last_tx'])
        except:
            return -1

    @property
    def length(self):
        try:
            return int(self._info_dict[self.local_disc]['length'])
        except:
            return -1

    @property
    def local_diag(self):
        try:
            return int(self._info_dict[self.local_disc]['local_diag'])
        except:
            return -1

    @property
    def local_multi(self):
        try:
            return int(self._info_dict[self.local_disc]['local_multi'])
        except:
            return -1


    @property
    def local_state(self):
        try:
            return self._info_dict[self.local_disc]['local_state']
        except:
            return 'na'

    @property
    def min_echo_interval(self):
        try:
            return int(self._info_dict[self.local_disc]['min_echo_interval'])
        except:
            return -1

    @property
    def min_rx(self):
        try:
            return int(self._info_dict[self.local_disc]['min_rx'])
        except:
            return -1

    @property
    def min_tx(self):
        try:
            return (self._info_dict[self.local_disc]['min_tx'])
        except:
            return -1

    @property
    def min_tx_interval(self):
        try:
            return int(self._info_dict[self.local_disc]['min_tx_interval'])
        except:
            return -1

    @property
    def multiplier(self):
        try:
            return int(self._info_dict[self.local_disc]['multiplier'])
        except:
            return -1


    @property
    def my_disc(self):
        try:
            return int(self._info_dict[self.local_disc]['my_disc'])
        except:
            return -1

    @property
    def no_host_reason(self):
        try:
            return self._info_dict[self.local_disc]['no_host_reason']
        except:
            return 'na'

    @property
    def out_str(self):
        try:
            return self._info_dict[self.local_disc]['out_str']
        except:
            return 'na'

    @property
    def parent(self):
        try:
            return int(self._info_dict[self.local_disc]['parent'])
        except:
            return -1

    @property
    def per_link_str(self):
        try:
            return self._info_dict[self.local_disc]['per_link_str']
        except:
            return 'na'

    @property
    def poll(self):
        try:
            return int(self._info_dict[self.local_disc]['poll'])
        except:
            return -1

    @property
    def poll_bit(self):
        try:
            return int(self._info_dict[self.local_disc]['poll_bit'])
        except:
            return -1

    @property
    def print_details(self):
        try:
            return int(self._info_dict[self.local_disc]['print_details'])
        except:
            return -1

    @property
    def remote_disc(self):
        try:
            return self._info_dict[self.local_disc]['remote_disc']
        except:
            return 'na'

    @property
    def remote_state(self):
        try:
            return self._info_dict[self.local_disc]['remote_state']
        except:
            return 'na'

    @property
    def req_min_rx(self):
        try:
            return int(self._info_dict[self.local_disc]['req_min_rx'])
        except:
            return -1

    @property
    def rx_avg(self):
        try:
            return int(self._info_dict[self.local_disc]['rx_avg'])
        except:
            return -1

    @property
    def rx_count(self):
        try:
            return int(self._info_dict[self.local_disc]['rx_count'])
        except:
            return -1

    @property
    def rx_max(self):
        try:
            return int(self._info_dict[self.local_disc]['rx_max'])
        except:
            return -1

    @property
    def rx_min(self):
        try:
            return int(self._info_dict[self.local_disc]['rx_min'])
        except:
            return -1

    @property
    def src_ip_addr(self):
        try:
            return self._info_dict[self.local_disc]['src_ip_addr']
        except:
            return 'na'

    @property
    def src_ipv6_addr(self):
        try:
            return self._info_dict[self.local_disc]['src_ipv6_addr']
        except:
            return 'na'

    @property
    def state_bit(self):
        try:
            return self._info_dict[self.local_disc]['state_bit']
        except:
            return 'na'

    @property
    def tx_avg(self):
        try:
            return int(self._info_dict[self.local_disc]['tx_avg'])
        except:
            return -1

    @property
    def tx_count(self):
        try:
            return int(self._info_dict[self.local_disc]['tx_count'])
        except:
            return -1

    @property
    def tx_interval(self):
        try:
            return int(self._info_dict[self.local_disc]['tx_interval'])
        except:
            return -1

    @property
    def tx_max(self):
        try:
            return int(self._info_dict[self.local_disc]['tx_max'])
        except:
            return -1

    @property
    def tx_min(self):
        try:
            return int(self._info_dict[self.local_disc]['tx_min'])
        except:
            return -1

    @property
    def up_time(self):
        try:
            return int(self._info_dict[self.local_disc]['up_time'])
        except:
            return -1

    @property
    def version(self):
        try:
            return int(self._info_dict[self.local_disc]['version'])
        except:
            return -1

    @property
    def vrf_name(self):
        try:
            return self._info_dict[self.local_disc]['vrf_name']
        except:
            return 'na'

    @property
    def your_disc(self):
        try:
            return int(self._info_dict[self.local_disc]['your_disc'])
        except:
            return -1



