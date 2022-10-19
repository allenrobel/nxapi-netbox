#!/usr/bin/env python3
'''
Name: nxapi_interface.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving interface information via NXAPI

Synopsis:

from general.log import get_logger
from nxapi.nxapi_interface import NxapiInterface

script_name = 'nxapi_interface_info'

def get_max_width(d):
    width = 0
    for key in d:
        if len(key) > width:
            width = len(key)
    return width

def print_prop(hostname, interface, width, key, value):
    print("{:<15} {:<15} {:<{width}} {:<}".format(hostname, interface, key, value, width=width))

def print_dict(d, hostname, width):
    for peer in d:
        for key in sorted(d[peer]):
            value = d[peer][key]
            if type(value) != type(dict()):
                print("{:<15} {:<15} {:<{width}} {}".format(hostname, peer, key, value, width=width))
                continue
            for k in value:
                print("{:<15} {:<15} {:<{width}} {}".format(hostname, peer, k, value[k], width=width))
        print()

log = get_logger(script_name, cfg.loglevel, 'DEBUG')
i = NxapiInterface('admin', 'mypassword', '10.1.1.1', log)
i.interface = 'Eth1/1'
i.nxapi_init(cfg)
i.refresh()
width = get_max_width(i.info)
print_dict(i.info, i.hostname, width)
print_prop(i.hostname, i.interface, width, 'interface', i.interface)
print_prop(i.hostname, i.interface, width, 'state', i.state)
# <etc, for other supported properties>

i = NxapiInterfaceAll(cfg.username, cfg.password, '10.1.1.1', log)
i.nxapi_init(cfg)
i.refresh()
width = get_max_width(i.info)
for interface in i.interface_list:
    i.interface = interface
    print_dict(i.interface_counters, i.hostname, width)
    print_prop(i.hostname, i.interface, width, 'interface', i.interface)
    print_prop(i.hostname, i.interface, width, 'state', i.state)
    # <etc, for other supported properties>



Examples of json data returned for various interface types.

switch# sh inter Eth1/1 | json-pretty
{
    "TABLE_interface": {
        "ROW_interface": {
            "interface": "Ethernet1/1", 
            "state": "down", 
            "state_rsn_desc": "XCVR not inserted", 
            "admin_state": "down", 
            "share_state": "Dedicated", 
            "eth_hw_desc": "100/1000/10000/25000 Ethernet", 
            "eth_hw_addr": "006b.f137.5a5d", 
            "eth_bia_addr": "006b.f137.5a5e", 
            "eth_mtu": "1500", 
            "eth_bw": "25000000", 
            "eth_dly": "10", 
            "eth_reliability": "255", 
            "eth_txload": "1", 
            "eth_rxload": "1", 
            "medium": "broadcast", 
            "eth_duplex": "auto", 
            "eth_speed": "auto-speed", 
            "eth_beacon": "off", 
            "eth_autoneg": "on", 
            "eth_in_flowctrl": "off", 
            "eth_out_flowctrl": "off", 
            "eth_mdix": "off", 
            "eth_swt_monitor": "off", 
            "eth_ethertype": "0x8100", 
            "eth_eee_state": "n/a", 
            "eth_link_flapped": "never", 
            "eth_clear_counters": "never", 
            "eth_reset_cntr": "0", 
            "eth_load_interval1_rx": "30", 
            "eth_inrate1_bits": "0", 
            "eth_inrate1_pkts": "0", 
            "eth_load_interval1_tx": "30", 
            "eth_outrate1_bits": "0", 
            "eth_outrate1_pkts": "0", 
            "eth_inucast": "0", 
            "eth_inmcast": "0", 
            "eth_inbcast": "0", 
            "eth_inpkts": "0", 
            "eth_inbytes": "0", 
            "eth_jumbo_inpkts": "0", 
            "eth_storm_supp": "0", 
            "eth_runts": "0", 
            "eth_giants": "0", 
            "eth_crc": "0", 
            "eth_nobuf": "0", 
            "eth_inerr": "0", 
            "eth_frame": "0", 
            "eth_overrun": "0", 
            "eth_underrun": "0", 
            "eth_ignored": "0", 
            "eth_watchdog": "0", 
            "eth_bad_eth": "0", 
            "eth_bad_proto": "0", 
            "eth_in_ifdown_drops": "0", 
            "eth_dribble": "0", 
            "eth_indiscard": "0", 
            "eth_inpause": "0", 
            "eth_outucast": "0", 
            "eth_outmcast": "0", 
            "eth_outbcast": "0", 
            "eth_outpkts": "0", 
            "eth_outbytes": "0", 
            "eth_jumbo_outpkts": "0", 
            "eth_outerr": "0", 
            "eth_coll": "0", 
            "eth_deferred": "0", 
            "eth_latecoll": "0", 
            "eth_lostcarrier": "0", 
            "eth_nocarrier": "0", 
            "eth_babbles": "0", 
            "eth_outdiscard": "0", 
            "eth_outpause": "0"
        }
    }
}
switch# 

switch# sh inter Vlan2001 | json-pretty
{
    "TABLE_interface": {
        "ROW_interface": {
            "interface": "Vlan2001", 
            "svi_admin_state": "up", 
            "svi_line_proto": "up", 
            "svi_mac": "006b.f137.5a5d", 
            "svi_ip_addr": "11.0.0.1", 
            "svi_ip_mask": "24", 
            "svi_mtu": "1500", 
            "svi_bw": "1000000", 
            "svi_delay": "10", 
            "svi_tx_load": "1", 
            "svi_rx_load": "1", 
            "svi_arp_type": "ARPA", 
            "svi_time_last_cleared": "never", 
            "svi_ucast_pkts_in": "0", 
            "svi_ucast_bytes_in": "0"
        }
    }
}
switch# sh inter nve1 | json-pretty
{
    "TABLE_interface": {
        "ROW_interface": {
            "interface": "nve1", 
            "state": "up", 
            "admin_state": "up", 
            "eth_hw_desc": "NVE", 
            "eth_mtu": "9216", 
            "eth_mdix": "off", 
            "nve_rx_ucastpkts": "292736484", 
            "nve_rx_ucastbytes": "452570604264", 
            "nve_rx_mcastpkts": "3494044", 
            "nve_rx_mcastbytes": "523026676", 
            "nve_tx_ucastpkts": "209650082", 
            "nve_tx_ucastbytes": "324119026772", 
            "nve_tx_mcastpkts": "2520207", 
            "nve_tx_mcastbytes": "282870542"
        }
    }
}
switch# 

NxapiInterface() uses the following when adding attributes for new interface types.

    # text-based @property template
    @property
    def ttt(self):
        try:
            return self._info_dict['ttt']
        except:
            return 'na'

    # integer-based @property template
    @property
    def iii(self):
        try:
            return int(self._info_dict['iii'])
        except:
            return -1


NxapiInterfaceAll() use the following when adding attributes for new interface types.

    # text-based @property template
    @property
    def ttt(self):
        try:
            return self.interface_counters['ttt']
        except:
            return 'na'

    # integer-based @property template
    @property
    def iii(self):
        try:
            return int(self.interface_counters['iii'])
        except:
            return -1

'''
our_version = 110

from nxapi.nxapi_base import NxapiBase
from general.util import NxTimer
class NxapiInterfaceStatus(NxapiBase):
    '''
    return a dictionary with the following structure:
        self.info[<interface1>]['interface'] = <interface>
        self.info[<interface1>]['state'] = <state>
        self.info[<interface1>]['vlan'] = <vlan or routed>
        self.info[<interface1>]['duplex'] = [auto | full | half]
        self.info[<interface1>]['speed'] = [auto | <speed>]
        self.info[<interface1>]['type'] = "--"
    The above is based on the json returned by 'show interface status | json-pretty'
            {
                "interface": "Ethernet1/3", 
                "state": "xcvrAbsent", 
                "vlan": "routed", 
                "duplex": "auto", 
                "speed": "auto", 
                "type": "--"
            }, 
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self.lib_name = 'NxapiInterfaceStatus'
        self.log_prefix = '{}_v{}'.format(self.lib_name, self.lib_version)
        self._interface = None
        self._info_dict = dict()
        self.refreshed = False

    def refresh(self):
        if self.interface == None:
            self.cli = 'show interface status'
        else:
            self.cli = 'show interface {} status'.format(self.interface)
        self.log.debug('{} {} using cli {}'.format(self.log_prefix, self.hostname, self.cli))
        self.show(self.cli)
        self.make_info_dict()

        for _key in self._info_dict:
            if 'interface' not in self._info_dict:
                return False
        self.refreshed = True
        return True

    def make_info_dict(self):
        self._info_dict = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        _list = self._get_table_row('interface', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            try:
                interface = _dict['interface']
            except:
                self.log.debug('{} [interface] key not in _dict {}'.format(self.hostname, _dict))
                return
            self._info_dict[interface] = _dict

    @property
    def duplex(self):
        '''
        i.refresh()
        i.interface = 'Ethernet1/1'
        print('Ethernet1/1 duplex {}'.format(i.duplex))
        '''
        try:
            return self.info[self._interface]['duplex']
        except Exception as e:
            self.log.debug('Exception was {}'.format(e))
            return 'na'

    @property
    def interface(self):
        return self._interface
    @interface.setter
    def interface(self, _x):
        self._interface = _x

    # @property returning dictionaries
    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        dict is keyed on iterface.  The value is a dict with the following format:
        {'interface': 'Ethernet1/34', 'state': 'xcvrAbsent', 'vlan': 'trunk', 'duplex': 'auto', 'speed': 'auto', 'type': '--'}
        '''
        try:
            return self._info_dict
        except:
            return dict()

    @property
    def speed(self):
        '''
        i.refresh()
        i.interface = 'Ethernet1/1'
        print('Ethernet1/1 speed {}'.format(i.speed))
        '''
        try:
            return self.info[self._interface]['speed']
        except Exception as e:
            self.log.debug('Exception was {}'.format(e))
            return 'na'

    @property
    def state(self):
        '''
        i.refresh()
        i.interface = 'Ethernet1/1'
        print('Ethernet1/1 state {}'.format(i.state))
        '''
        try:
            return self.info[self._interface]['state']
        except Exception as e:
            self.log.debug('Exception was {}'.format(e))
            return 'na'

    @property
    def type(self):
        '''
        i.refresh()
        i.interface = 'Ethernet1/1'
        print('Ethernet1/1 type {}'.format(i.type))
        '''
        try:
            return self.info[self._interface]['type']
        except Exception as e:
            self.log.debug('Exception was {}'.format(e))
            return 'na'

    @property
    def vlan(self):
        '''
        i.refresh()
        i.interface = 'Ethernet1/1'
        print('Ethernet1/1 vlan {}'.format(i.vlan))
        '''
        try:
            return self.info[self._interface]['vlan']
        except Exception as e:
            self.log.debug('Exception was {}'.format(e))
            return 'na'

class NxapiInterface(NxapiBase):
    '''
    NxapiInterface() is more efficient than NxapiInterfaceAll() if you want to get/monitor/process counters for a single interface.
    Use NxapiInterfaceAll() if you want to get/monitor/process counters for all interfaces.
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self.lib_name = 'NxapiInterface'
        self.log_prefix = '{}_v{}'.format(self.lib_name, self.lib_version)
        self._interface = None
        self._info_dict = dict()
        self.virtual_interfaces = ['vl', 'nv', 'po', 'lo', '.']
        self.refreshed = False
        self.nx_timer = NxTimer()

    def is_virtual_interface(self,interface):
        '''
        return True if interface is virtual e.g. Vlan10, Nve1, Po20, Eth1/1.100
        '''
        is_virtual = False
        for interface_substring in self.virtual_interfaces:
            #self.log.info('{} testing interface_substring {} interface {}'.format(self.log_prefix, interface_substring, interface.lower()))
            if interface_substring in interface.lower():
                is_virtual = True
        return is_virtual


    def refresh(self):
        if self.interface == None:
            self.log.error("{} {} early return: self.interface is not defined. Call instance.interface = <interface> first".format(self.log_prefix, self.hostname))
            return
        self.cli = 'show interface {}'.format(self.interface)
        self.show(self.cli)
        self.make_info_dict()

        for _key in self._info_dict:
            self.log.debug('{} {} interface {} key {} value {}'.format(self.log_prefix, self.hostname, self.interface, _key, self._info_dict[_key]))
        if 'interface' not in self._info_dict:
            return False
        self.refreshed = True
        return True


    def make_info_dict(self):
        self._info_dict = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        _list = self._get_table_row('interface', self.body[0])
        if _list == False:
            return
        _dict = _list[0]

        # since we currently support only a single interface, ROW_interface will be a dict()
        # We may convert to list() in the future if we decide to support multiple intefaces
        #_row_items = self._convert_to_list(_dict)
        if not self.verify.is_dict(_dict):
            self.log.error('{} {} early return: Expected a dict() for {}. Got {}'.format(type(self.log_prefix, self.hostname, self.interface, type(_dict))))
            return
        if 'interface' not in _dict:
            self.log.debug('{} {} skipping {}. [interface] key not in _dict {}'.format(self.log_prefix, self.hostname, self.interface, _dict))
            self._info_dict = dict()
            return
        self._info_dict = _dict

    @property
    def errors(self):
        '''
        returns a dictionary, keyed on interface error type
        values are the value for each interface error type 
        '''
        self.error_dict = dict()
        self.error_dict['eth_outdiscard'] = self.eth_outdiscard
        self.error_dict['eth_babbles'] = self.eth_babbles
        self.error_dict['eth_nocarrier'] = self.eth_nocarrier
        self.error_dict['eth_lostcarrier'] = self.eth_lostcarrier
        self.error_dict['eth_latecoll'] = self.eth_latecoll
        self.error_dict['eth_deferred'] = self.eth_deferred
        self.error_dict['eth_coll'] = self.eth_coll
        self.error_dict['eth_outerr'] = self.eth_outerr
        self.error_dict['eth_indiscard'] = self.eth_indiscard
        self.error_dict['eth_dribble'] = self.eth_dribble
        self.error_dict['eth_in_ifdown_drops'] = self.eth_in_ifdown_drops
        self.error_dict['eth_bad_proto'] = self.eth_bad_proto
        self.error_dict['eth_bad_eth'] = self.eth_bad_eth
        self.error_dict['eth_watchdog'] = self.eth_watchdog
        self.error_dict['eth_ignored'] = self.eth_ignored
        self.error_dict['eth_underrun'] = self.eth_underrun
        self.error_dict['eth_overrun'] = self.eth_overrun
        self.error_dict['eth_frame'] = self.eth_frame
        self.error_dict['eth_inerr'] = self.eth_inerr
        self.error_dict['eth_nobuf'] = self.eth_nobuf
        self.error_dict['eth_crc'] = self.eth_crc
        self.error_dict['eth_giants'] = self.eth_giants
        self.error_dict['eth_runts'] = self.eth_runts
        return self.error_dict

    @property
    def interface(self):
        return self._interface
    @interface.setter
    def interface(self, _x):
        self._interface = _x

    # @property returning dictionaries
    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info_dict
        except:
            return dict()

    # @properties for ethernet interfaces

    @property
    def eth_outpause(self):
        try:
            return int(self._info_dict['eth_outpause'])
        except:
            return -1

    @property
    def eth_outdiscard(self):
        try:
            return int(self._info_dict['eth_outdiscard'])
        except:
            return -1

    @property
    def eth_babbles(self):
        try:
            return int(self._info_dict['eth_babbles'])
        except:
            return -1

    @property
    def eth_nocarrier(self):
        try:
            return int(self._info_dict['eth_nocarrier'])
        except:
            return 'na'

    @property
    def eth_lostcarrier(self):
        try:
            return int(self._info_dict['eth_lostcarrier'])
        except:
            return -1

    @property
    def eth_latecoll(self):
        try:
            return int(self._info_dict['eth_latecoll'])
        except:
            return -1

    @property
    def eth_deferred(self):
        try:
            return int(self._info_dict['eth_deferred'])
        except:
            return -1

    @property
    def eth_coll(self):
        try:
            return int(self._info_dict['eth_coll'])
        except:
            return -1

    @property
    def eth_outerr(self):
        try:
            return int(self._info_dict['eth_outerr'])
        except:
            return -1

    @property
    def eth_jumbo_outpkts(self):
        try:
            return int(self._info_dict['eth_jumbo_outpkts'])
        except:
            return -1

    @property
    def eth_outbytes(self):
        try:
            return int(self._info_dict['eth_outbytes'])
        except:
            return -1

    @property
    def eth_outpkts(self):
        try:
            return int(self._info_dict['eth_outpkts'])
        except:
            return -1

    @property
    def eth_outbcast(self):
        try:
            return int(self._info_dict['eth_outbcast'])
        except:
            return -1

    @property
    def eth_outmcast(self):
        try:
            return int(self._info_dict['eth_outmcast'])
        except:
            return -1

    @property
    def eth_outucast(self):
        try:
            return int(self._info_dict['eth_outucast'])
        except:
            return -1

    @property
    def eth_inpause(self):
        try:
            return int(self._info_dict['eth_inpause'])
        except:
            return -1

    @property
    def eth_indiscard(self):
        try:
            return int(self._info_dict['eth_indiscard'])
        except:
            return -1

    @property
    def eth_dribble(self):
        try:
            return int(self._info_dict['eth_dribble'])
        except:
            return -1

    @property
    def eth_in_ifdown_drops(self):
        try:
            return int(self._info_dict['eth_in_ifdown_drops'])
        except:
            return -1

    @property
    def eth_bad_proto(self):
        try:
            return int(self._info_dict['eth_bad_proto'])
        except:
            return -1

    @property
    def eth_bad_eth(self):
        try:
            return int(self._info_dict['eth_bad_eth'])
        except:
            return -1

    @property
    def eth_watchdog(self):
        try:
            return int(self._info_dict['eth_watchdog'])
        except:
            return -1

    @property
    def eth_ignored(self):
        try:
            return int(self._info_dict['eth_ignored'])
        except:
            return -1

    @property
    def eth_underrun(self):
        try:
            return int(self._info_dict['eth_underrun'])
        except:
            return -1

    @property
    def eth_overrun(self):
        try:
            return int(self._info_dict['eth_overrun'])
        except:
            return -1

    @property
    def eth_frame(self):
        try:
            return int(self._info_dict['eth_frame'])
        except:
            return -1

    @property
    def eth_inerr(self):
        try:
            return int(self._info_dict['eth_inerr'])
        except:
            return -1

    @property
    def eth_nobuf(self):
        try:
            return int(self._info_dict['eth_nobuf'])
        except:
            return -1

    @property
    def eth_crc(self):
        try:
            return int(self._info_dict['eth_crc'])
        except:
            return -1

    @property
    def eth_giants(self):
        try:
            return int(self._info_dict['eth_giants'])
        except:
            return -1

    @property
    def eth_runts(self):
        try:
            return int(self._info_dict['eth_runts'])
        except:
            return -1

    @property
    def eth_storm_supp(self):
        try:
            return int(self._info_dict['eth_storm_supp'])
        except:
            return -1

    @property
    def eth_jumbo_inpkts(self):
        try:
            return int(self._info_dict['eth_jumbo_inpkts'])
        except:
            return -1

    @property
    def eth_inbytes(self):
        try:
            return int(self._info_dict['eth_inbytes'])
        except:
            return -1

    @property
    def eth_inpkts(self):
        try:
            return int(self._info_dict['eth_inpkts'])
        except:
            return -1

    @property
    def eth_inbcast(self):
        try:
            return int(self._info_dict['eth_inbcast'])
        except:
            return -1

    @property
    def eth_inmcast(self):
        try:
            return int(self._info_dict['eth_inmcast'])
        except:
            return -1

    @property
    def eth_inucast(self):
        try:
            return int(self._info_dict['eth_inucast'])
        except:
            return -1

    @property
    def eth_outrate1_pkts(self):
        try:
            return int(self._info_dict['eth_outrate1_pkts'])
        except:
            return -1

    @property
    def eth_outrate1_bits(self):
        try:
            return int(self._info_dict['eth_outrate1_bits'])
        except:
            return -1

    @property
    def eth_load_interval1_tx(self):
        try:
            return int(self._info_dict['eth_load_interval1_tx'])
        except:
            return -1

    @property
    def eth_inrate1_pkts(self):
        try:
            return int(self._info_dict['eth_inrate1_pkts'])
        except:
            return -1

    @property
    def eth_inrate1_bits(self):
        try:
            return int(self._info_dict['eth_inrate1_bits'])
        except:
            return -1

    @property
    def eth_load_interval1_rx(self):
        try:
            return int(self._info_dict['eth_load_interval1_rx'])
        except:
            return -1

    @property
    def eth_reset_cntr(self):
        try:
            return self._info_dict['eth_reset_cntr']
        except:
            return -1.0

    @property
    def eth_clear_counters(self):
        try:
            self.nx_timer.refresh(self._info_dict['eth_clear_counters'])
            return self.nx_timer.timer2sec
        except:
            return -1.0

    @property
    def eth_link_flapped(self):
        try:
            self.nx_timer.refresh(self._info_dict['eth_link_flapped'])
            return self.nx_timer.timer2sec
        except:
            return -1

    @property
    def eth_eee_state(self):
        try:
            return self._info_dict['eth_eee_state']
        except:
            return 'na'

    @property
    def eth_ethertype(self):
        try:
            return self._info_dict['eth_ethertype']
        except:
            return 'na'

    @property
    def eth_swt_monitor(self):
        try:
            return self._info_dict['eth_swt_monitor']
        except:
            return 'na'

    @property
    def eth_mdix(self):
        try:
            return int(self._info_dict['eth_mdix'])
        except:
            return 'na'

    @property
    def eth_out_flowctrl(self):
        try:
            return self._info_dict['eth_out_flowctrl']
        except:
            return 'na'

    @property
    def eth_in_flowctrl(self):
        try:
            return self._info_dict['eth_in_flowctrl']
        except:
            return 'na'

    @property
    def eth_autoneg(self):
        try:
            return self._info_dict['eth_autoneg']
        except:
            return 'na'

    @property
    def eth_beacon(self):
        try:
            return self._info_dict['eth_beacon']
        except:
            return 'na'

    @property
    def eth_speed(self):
        try:
            return self._info_dict['eth_speed']
        except:
            return 'na'

    @property
    def eth_duplex(self):
        try:
            return self._info_dict['eth_duplex']
        except:
            return 'na'

    @property
    def medium(self):
        try:
            return self._info_dict['medium']
        except:
            return 'na'

    @property
    def eth_rxload(self):
        try:
            return int(self._info_dict['eth_rxload'])
        except:
            return -1

    @property
    def eth_txload(self):
        try:
            return int(self._info_dict['eth_txload'])
        except:
            return -1

    @property
    def eth_reliability(self):
        try:
            return int(self._info_dict['eth_reliability'])
        except:
            return -1

    @property
    def eth_dly(self):
        try:
            return int(self._info_dict['eth_dly'])
        except:
            return -1

    @property
    def eth_bw(self):
        try:
            return int(self._info_dict['eth_bw'])
        except:
            return -1

    @property
    def eth_mtu(self):
        try:
            return int(self._info_dict['eth_mtu'])
        except:
            return -1

    @property
    def eth_bia_addr(self):
        try:
            return self._info_dict['eth_bia_addr']
        except:
            return 'na'

    @property
    def eth_hw_addr(self):
        try:
            return self._info_dict['eth_hw_addr']
        except:
            return 'na'

    @property
    def eth_hw_desc(self):
        try:
            return self._info_dict['eth_hw_desc']
        except:
            return 'na'

    @property
    def share_state(self):
        try:
            return self._info_dict['share_state']
        except:
            return 'na'

    @property
    def admin_state(self):
        try:
            return self._info_dict['admin_state']
        except:
            return 'na'

    @property
    def state_rsn_desc(self):
        try:
            return self._info_dict['state_rsn_desc']
        except:
            return 'na'

    @property
    def state(self):
        try:
            return self._info_dict['state']
        except:
            return 'na'



class NxapiInterfaceAll(NxapiBase):
    '''
    NxapiInterfaceAll() is more efficient than NxapiInterface() if you want to get counters for all interfaces.
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.lib_version = our_version
        self.lib_name = 'NxapiInterfaceAll'
        self.log_prefix = '{}_v{}'.format(self.lib_name, self.lib_version)
        self._info_dict = dict()
        self._interface_list = list()
        self._interface = None
        self.virtual_interfaces = ['vl', 'nv', 'po', 'lo', '.']
        self.refreshed = False
        self.nx_timer = NxTimer()
        self.default_interface_dict = {
            'interface': 'na',
            'state': 'na',
            'admin_state': 'na',
            'share_state': 'na',
            'eth_hw_desc': 'na',
            'eth_hw_addr': 'na',
            'eth_bia_addr': 'na',
            'eth_mtu': 'na',
            'eth_bw': -1,
            'eth_dly': -1,
            'eth_reliability': 'na',
            'eth_txload': 'na',
            'eth_rxload': 'na',
            'encapsulation': 'na',
            'medium': 'na',
            'eth_duplex': 'na',
            'eth_speed': 'na',
            'eth_media': 'na',
            'eth_beacon': 'na',
            'eth_autoneg': 'na',
            'eth_in_flowctrl': 'na',
            'eth_out_flowctrl': 'na',
            'eth_mdix': 'na',
            'eth_ratemode': 'na',
            'eth_swt_monitor': 'na',
            'eth_ethertype': 'na',
            'eth_eee_state': 'na',
            'eth_admin_fec_state': 'na',
            'eth_oper_fec_state': 'na',
            'eth_link_flapped': 'na',
            'eth_clear_counters': 'na',
            'eth_reset_cntr': -1,
            'eth_load_interval1_rx': -1,
            'eth_inrate1_bits': 'na',
            'eth_inrate1_pkts': 'na',
            'eth_load_interval1_tx': 'na',
            'eth_outrate1_bits': 'na',
            'eth_outrate1_pkts': 'na',
            'eth_inrate1_summary_bits': 'na',
            'eth_inrate1_summary_pkts': 'na',
            'eth_outrate1_summary_bits': 'na',
            'eth_outrate1_summary_pkts': 'na',
            'eth_load_interval2_rx': 'na',
            'eth_inrate2_bits': 'na',
            'eth_inrate2_pkts': 'na',
            'eth_load_interval2_tx': 'na',
            'eth_outrate2_bits': 'na',
            'eth_outrate2_pkts': 'na',
            'eth_inrate2_summary_bits': 'na',
            'eth_inrate2_summary_pkts': 'na',
            'eth_outrate2_summary_bits': 'na',
            'eth_outrate2_summary_pkts': 'na',
            'eth_inucast': -1,
            'eth_inmcast': -1,
            'eth_inbcast': -1,
            'eth_inpkts': -1,
            'eth_inbytes': -1,
            'eth_jumbo_inpkts': 'na',
            'eth_storm_supp': 'na',
            'eth_runts': -1,
            'eth_giants': -1,
            'eth_crc': 'na',
            'eth_nobuf': -1,
            'eth_inerr': 'na',
            'eth_frame': 'na',
            'eth_overrun': 'na',
            'eth_underrun': 'na',
            'eth_ignored': 'na',
            'eth_watchdog': 'na',
            'eth_bad_eth': 'na',
            'eth_bad_proto': 'na',
            'eth_in_ifdown_drops': 'na',
            'eth_dribble': 'na',
            'eth_indiscard': 'na',
            'eth_inpause': 'na',
            'eth_outucast': -1,
            'eth_outmcast': -1,
            'eth_outbcast': -1,
            'eth_outpkts': -1,
            'eth_outbytes': -1,
            'eth_jumbo_outpkts': 'na',
            'eth_outerr': 'na',
            'eth_coll': 'na',
            'eth_deferred': 'na',
            'eth_latecoll': 'na',
            'eth_lostcarrier': 'na',
            'eth_nocarrier': 'na',
            'eth_babbles': 'na',
            'eth_outdiscard': 'na',
            'eth_outpause': 'na'}

    def is_virtual_interface(self,interface):
        '''
        return True if interface is virtual e.g. Vlan10, Nve1, Po20, Eth1/1.100
        '''
        is_virtual = False
        for interface_substring in self.virtual_interfaces:
            #self.log.info('{} testing interface_substring {} interface {}'.format(self.log_prefix, interface_substring, interface.lower()))
            if interface_substring in interface.lower():
                is_virtual = True
        return is_virtual


    def refresh(self):
        self.cli = 'show interface'
        self.show(self.cli)
        self.make_info_dict()
        self.refreshed = True
        return True



    def make_info_dict(self):
        self._info_dict = dict()
        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        _list = self._get_table_row('interface', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'interface' not in _dict:
                continue
            self._info_dict[_dict['interface']] = _dict
            self._interface_list.append(_dict['interface'])

    @property
    def interface_list(self):
        try:
            return self._interface_list
        except:
            return list()

    @property
    def errors(self):
        '''
        returns a dictionary, keyed on interface error type
        values are the value for each interface error type 
        '''
        if self.interface == None:
            self.log.error('Returning default_interface_dict. Please set interface first.')
            return self.default_interface_dict
        self.error_dict = dict()
        self.error_dict['eth_outdiscard'] = self.eth_outdiscard
        self.error_dict['eth_babbles'] = self.eth_babbles
        self.error_dict['eth_nocarrier'] = self.eth_nocarrier
        self.error_dict['eth_lostcarrier'] = self.eth_lostcarrier
        self.error_dict['eth_latecoll'] = self.eth_latecoll
        self.error_dict['eth_deferred'] = self.eth_deferred
        self.error_dict['eth_coll'] = self.eth_coll
        self.error_dict['eth_outerr'] = self.eth_outerr
        self.error_dict['eth_indiscard'] = self.eth_indiscard
        self.error_dict['eth_dribble'] = self.eth_dribble
        self.error_dict['eth_in_ifdown_drops'] = self.eth_in_ifdown_drops
        self.error_dict['eth_bad_proto'] = self.eth_bad_proto
        self.error_dict['eth_bad_eth'] = self.eth_bad_eth
        self.error_dict['eth_watchdog'] = self.eth_watchdog
        self.error_dict['eth_ignored'] = self.eth_ignored
        self.error_dict['eth_underrun'] = self.eth_underrun
        self.error_dict['eth_overrun'] = self.eth_overrun
        self.error_dict['eth_frame'] = self.eth_frame
        self.error_dict['eth_inerr'] = self.eth_inerr
        self.error_dict['eth_nobuf'] = self.eth_nobuf
        self.error_dict['eth_crc'] = self.eth_crc
        self.error_dict['eth_giants'] = self.eth_giants
        self.error_dict['eth_runts'] = self.eth_runts
        return self.error_dict

    @property
    def interface(self):
        return self._interface
    @interface.setter
    def interface(self, _x):
        if self.refreshed == False:
            self.log.error('early return.  Please call instance.refresh() first')
        self._interface = _x
        try:
            self._interface_dict = self.info[_x]
        except:
            self._interface_dict = self.default_interface_dict

    @property
    def interface_counters(self):
        '''
        returns a dictionary containing counters for a single interface
        Usage:
        instance = NxapiInterfaceAll(<calling parameters>)
        instance.nxapi_init(<argparse instance>)
        instance.refresh()
        instance.interface = "Ethernet2/1"
        counters_dict = instance.interface_counters
        '''
        if self.refreshed == False:
            self.log.error('early return.  Please call instance.refresh() first')
        if self.interface == None:
            self.log.error('early return.  Please call instance.interface first. Example foo.interface = "Ethernet2/1"')
        return self._interface_dict

    # @property returning dictionaries
    @property
    def info(self):
        '''
        return the main dictionary created by this library self._info_dict
        '''
        try:
            return self._info_dict
        except:
            return dict()

    # @properties for ethernet interfaces

    @property
    def eth_outpause(self):
        try:
            return int(self.interface_counters['eth_outpause'])
        except:
            return -1

    @property
    def eth_outdiscard(self):
        try:
            return int(self.interface_counters['eth_outdiscard'])
        except:
            return -1

    @property
    def eth_babbles(self):
        try:
            return int(self.interface_counters['eth_babbles'])
        except:
            return -1

    @property
    def eth_nocarrier(self):
        try:
            return int(self.interface_counters['eth_nocarrier'])
        except:
            return 'na'

    @property
    def eth_lostcarrier(self):
        try:
            return int(self.interface_counters['eth_lostcarrier'])
        except:
            return -1

    @property
    def eth_latecoll(self):
        try:
            return int(self.interface_counters['eth_latecoll'])
        except:
            return -1

    @property
    def eth_deferred(self):
        try:
            return int(self.interface_counters['eth_deferred'])
        except:
            return -1

    @property
    def eth_coll(self):
        try:
            return int(self.interface_counters['eth_coll'])
        except:
            return -1

    @property
    def eth_outerr(self):
        try:
            return int(self.interface_counters['eth_outerr'])
        except:
            return -1

    @property
    def eth_jumbo_outpkts(self):
        try:
            return int(self.interface_counters['eth_jumbo_outpkts'])
        except:
            return -1

    @property
    def eth_outbytes(self):
        try:
            return int(self.interface_counters['eth_outbytes'])
        except:
            return -1

    @property
    def eth_outpkts(self):
        try:
            return int(self.interface_counters['eth_outpkts'])
        except:
            return -1

    @property
    def eth_outbcast(self):
        try:
            return int(self.interface_counters['eth_outbcast'])
        except:
            return -1

    @property
    def eth_outmcast(self):
        try:
            return int(self.interface_counters['eth_outmcast'])
        except:
            return -1

    @property
    def eth_outucast(self):
        try:
            return int(self.interface_counters['eth_outucast'])
        except:
            return -1

    @property
    def eth_inpause(self):
        try:
            return int(self.interface_counters['eth_inpause'])
        except:
            return -1

    @property
    def eth_indiscard(self):
        try:
            return int(self.interface_counters['eth_indiscard'])
        except:
            return -1

    @property
    def eth_dribble(self):
        try:
            return int(self.interface_counters['eth_dribble'])
        except:
            return -1

    @property
    def eth_in_ifdown_drops(self):
        try:
            return int(self.interface_counters['eth_in_ifdown_drops'])
        except:
            return -1

    @property
    def eth_bad_proto(self):
        try:
            return int(self.interface_counters['eth_bad_proto'])
        except:
            return -1

    @property
    def eth_bad_eth(self):
        try:
            return int(self.interface_counters['eth_bad_eth'])
        except:
            return -1

    @property
    def eth_watchdog(self):
        try:
            return int(self.interface_counters['eth_watchdog'])
        except:
            return -1

    @property
    def eth_ignored(self):
        try:
            return int(self.interface_counters['eth_ignored'])
        except:
            return -1

    @property
    def eth_underrun(self):
        try:
            return int(self.interface_counters['eth_underrun'])
        except:
            return -1

    @property
    def eth_overrun(self):
        try:
            return int(self.interface_counters['eth_overrun'])
        except:
            return -1

    @property
    def eth_frame(self):
        try:
            return int(self.interface_counters['eth_frame'])
        except:
            return -1

    @property
    def eth_inerr(self):
        try:
            return int(self.interface_counters['eth_inerr'])
        except:
            return -1

    @property
    def eth_nobuf(self):
        try:
            return int(self.interface_counters['eth_nobuf'])
        except:
            return -1

    @property
    def eth_crc(self):
        try:
            return int(self.interface_counters['eth_crc'])
        except:
            return -1

    @property
    def eth_giants(self):
        try:
            return int(self.interface_counters['eth_giants'])
        except:
            return -1

    @property
    def eth_runts(self):
        try:
            return int(self.interface_counters['eth_runts'])
        except:
            return -1

    @property
    def eth_storm_supp(self):
        try:
            return int(self.interface_counters['eth_storm_supp'])
        except:
            return -1

    @property
    def eth_jumbo_inpkts(self):
        try:
            return int(self.interface_counters['eth_jumbo_inpkts'])
        except:
            return -1

    @property
    def eth_inbytes(self):
        try:
            return int(self.interface_counters['eth_inbytes'])
        except:
            return -1

    @property
    def eth_inpkts(self):
        try:
            return int(self.interface_counters['eth_inpkts'])
        except:
            return -1

    @property
    def eth_inbcast(self):
        try:
            return int(self.interface_counters['eth_inbcast'])
        except:
            return -1

    @property
    def eth_inmcast(self):
        try:
            return int(self.interface_counters['eth_inmcast'])
        except:
            return -1

    @property
    def eth_inucast(self):
        try:
            return int(self.interface_counters['eth_inucast'])
        except:
            return -1

    @property
    def eth_outrate1_pkts(self):
        try:
            return int(self.interface_counters['eth_outrate1_pkts'])
        except:
            return -1

    @property
    def eth_outrate1_bits(self):
        try:
            return int(self.interface_counters['eth_outrate1_bits'])
        except:
            return -1

    @property
    def eth_load_interval1_tx(self):
        try:
            return int(self.interface_counters['eth_load_interval1_tx'])
        except:
            return -1

    @property
    def eth_inrate1_pkts(self):
        try:
            return int(self.interface_counters['eth_inrate1_pkts'])
        except:
            return -1

    @property
    def eth_inrate1_bits(self):
        try:
            return int(self.interface_counters['eth_inrate1_bits'])
        except:
            return -1

    @property
    def eth_load_interval1_rx(self):
        try:
            return int(self.interface_counters['eth_load_interval1_rx'])
        except:
            return -1

    @property
    def eth_reset_cntr(self):
        try:
            return self.interface_counters['eth_reset_cntr']
        except:
            return -1.0

    @property
    def eth_clear_counters(self):
        try:
            self.nx_timer.refresh(self.interface_counters['eth_clear_counters'])
            return self.nx_timer.timer2sec
        except:
            return -1.0

    @property
    def eth_link_flapped(self):
        try:
            self.nx_timer.refresh(self.interface_counters['eth_link_flapped'])
            return self.nx_timer.timer2sec
        except:
            return -1

    @property
    def eth_eee_state(self):
        try:
            return self.interface_counters['eth_eee_state']
        except:
            return 'na'

    @property
    def eth_ethertype(self):
        try:
            return self.interface_counters['eth_ethertype']
        except:
            return 'na'

    @property
    def eth_swt_monitor(self):
        try:
            return self.interface_counters['eth_swt_monitor']
        except:
            return 'na'

    @property
    def eth_mdix(self):
        try:
            return int(self.interface_counters['eth_mdix'])
        except:
            return 'na'

    @property
    def eth_out_flowctrl(self):
        try:
            return self.interface_counters['eth_out_flowctrl']
        except:
            return 'na'

    @property
    def eth_in_flowctrl(self):
        try:
            return self.interface_counters['eth_in_flowctrl']
        except:
            return 'na'

    @property
    def eth_autoneg(self):
        try:
            return self.interface_counters['eth_autoneg']
        except:
            return 'na'

    @property
    def eth_beacon(self):
        try:
            return self.interface_counters['eth_beacon']
        except:
            return 'na'

    @property
    def eth_speed(self):
        try:
            return self.interface_counters['eth_speed']
        except:
            return 'na'

    @property
    def eth_duplex(self):
        try:
            return self.interface_counters['eth_duplex']
        except:
            return 'na'

    @property
    def medium(self):
        try:
            return self.interface_counters['medium']
        except:
            return 'na'

    @property
    def eth_rxload(self):
        try:
            return int(self.interface_counters['eth_rxload'])
        except:
            return -1

    @property
    def eth_txload(self):
        try:
            return int(self.interface_counters['eth_txload'])
        except:
            return -1

    @property
    def eth_reliability(self):
        try:
            return int(self.interface_counters['eth_reliability'])
        except:
            return -1

    @property
    def eth_dly(self):
        try:
            return int(self.interface_counters['eth_dly'])
        except:
            return -1

    @property
    def eth_bw(self):
        try:
            return int(self.interface_counters['eth_bw'])
        except:
            return -1

    @property
    def eth_mtu(self):
        try:
            return int(self.interface_counters['eth_mtu'])
        except:
            return -1

    @property
    def eth_bia_addr(self):
        try:
            return self.interface_counters['eth_bia_addr']
        except:
            return 'na'

    @property
    def eth_hw_addr(self):
        try:
            return self.interface_counters['eth_hw_addr']
        except:
            return 'na'

    @property
    def eth_hw_desc(self):
        try:
            return self.interface_counters['eth_hw_desc']
        except:
            return 'na'

    @property
    def share_state(self):
        try:
            return self.interface_counters['share_state']
        except:
            return 'na'

    @property
    def admin_state(self):
        try:
            return self.interface_counters['admin_state']
        except:
            return 'na'

    @property
    def state_rsn_desc(self):
        try:
            return self.interface_counters['state_rsn_desc']
        except:
            return 'na'

    @property
    def state(self):
        try:
            return self.interface_counters['state']
        except:
            return 'na'

