#!/usr/bin/env python3
our_version = 102
# NxapiBgpL2vpnEvpnSummary() - nxapi_bgp_l2vpn_evpn_summary.py
# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase
'''
Name: nxapi_bgp_l2vpn_evpn_summary.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes for retrieving bgp l2vpn evpn summary information 

NOTES:

Assumes the following JSON:

switch# sh bgp l2vpn evpn summary  | json-pretty 
{
    "TABLE_vrf": {
        "ROW_vrf": {
            "vrf-name-out": "default", 
            "vrf-router-id": "10.239.0.0", 
            "vrf-local-as": "65001", 
            "TABLE_af": {
                "ROW_af": {
                    "af-id": "25", 
                    "TABLE_saf": {
                        "ROW_saf": {
                            "safi": "70", 
                            "af-name": "L2VPN EVPN", 
                            "tableversion": "1967", 
                            "configuredpeers": "2", 
                            "capablepeers": "2", 
                            "totalnetworks": "136", 
                            "totalpaths": "198", 
                            "memoryused": "31200", 
                            "numberattrs": "143", 
                            "bytesattrs": "26312", 
                            "numberpaths": "1", 
                            "bytespaths": "6", 
                            "numbercommunities": "0", 
                            "bytescommunities": "0", 
                            "numberclusterlist": "10", 
                            "bytesclusterlist": "40", 
                            "dampening": "false", 
                            "TABLE_neighbor": {
                                "ROW_neighbor": [
                                    {
                                        "neighborid": "10.239.0.8", 
                                        "neighborversion": "4", 
                                        "msgrecvd": "633", 
                                        "msgsent": "397", 
                                        "neighbortableversion": "1967", 
                                        "inq": "0", 
                                        "outq": "0", 
                                        "neighboras": "65001", 
                                        "time": "PT4H37M19S", 
                                        "state": "Established", 
                                        "prefixreceived": "52"
                                    }, 
                                    {
                                        "neighborid": "10.239.0.9", 
                                        "neighborversion": "4", 
                                        "msgrecvd": "456", 
                                        "msgsent": "405", 
                                        "neighbortableversion": "1967", 
                                        "inq": "0", 
                                        "outq": "0", 
                                        "neighboras": "65001", 
                                        "time": "PT6H35M5S", 
                                        "state": "Established", 
                                        "prefixreceived": "52"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
}
switch#  

'''

class NxapiBgpL2vpnEvpnSummary(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._vrf = None
        self.bgp_afi = 25
        self.bgp_safi = 70
        self.cli = None
        self._neighbor = None
        self._vrf_dict = dict()
        self._afi_dict = dict()
        self._safi_dict = dict()
        self._neighbor_dict = dict()

        self._neighborid = None
        self._neighborversion = None
        self._msgrecvd = None 
        self._msgsent = None
        self._neighbortableversion = None
        self._inq = None
        self._outq = None
        self._neighboras = None
        self._time = None
        self._state = None
        self._prefixreceived = None


    def refresh(self):
        if self.vrf == None:
            self.vrf = 'default'
        self.cli = 'show bgp l2vpn evpn summary vrf {}'.format(self.vrf)
        self.show(self.cli)
        self.log.debug('self.cli {}'.format(self.cli))
        # order of calls below is important
        self.make_vrf_info()
        self.make_afi_info()
        self.make_safi_info()
        self.make_neighbor_info()

    def make_vrf_info(self):
        '''
        populates self.vrf_info dict() if vrf-name-out == self.vrf
        '''
        if self.vrf == None:
            self.log.error('{} Exiting. Please set instance.vrf before call instance.refresh()'.format(self.hostname))
            exit(1)
        self._vrf_info = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if 'vrf-name-out' not in _dict:
                continue
            if _dict['vrf-name-out'] != self.vrf:
                continue
            self._vrf_info = _dict

    def make_afi_info(self):
        '''
        populates self.afi_info dict() for af-id == self.bgp_afi
        '''
        self._afi_info = dict()
        if len(self.vrf_info) == 0:
            self.log.warning('{} Setting empty self.afi_info due to self.vrf_info is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('af', self.vrf_info)
        if _list == False:
            return
        for _dict in _list:
            if 'af-id' not in _dict:
                self.log.debug('{} Skipping due to key [af-id] not found in _dict {}'.format(self.hostname, _dict))
                continue
            if _dict['af-id'] == str(self.bgp_afi):
                self._afi_info = _dict
                return
        self.log.warning('{} Setting empty self.afi_info due to afi ({}) [af-id] not found.'.format(self.bgp_afi, self.hostname))

    def make_safi_info(self):

        '''
        populates self.safi_info dict() for safi == 1
        '''
        self._safi_info = dict()
        if len(self.afi_info) == 0:
            self.log.warning('{} Setting empty self.safi_info due to self.afi_info is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('saf', self.afi_info)
        if _list == False:
            return
        for _dict in _list:
            if 'safi' not in _dict:
                self.log.debug('{} Skipping due to key [safi] not found in _dict {}'.format(self.hostname, _dict))
                continue
            if _dict['safi'] == self.bgp_safi:
                self._safi_info = _dict
                return
        self.log.warning('{} Setting empty self.safi_info due to evpn safi (70) not found'.format(self.hostname))


    def make_neighbor_list(self):

        '''
        returns the list of neighbor dict() from ROW_neighbor
        '''
        self.neighbor_list = list()
        if len(self.safi_info) == 0:
            self.log.warning('{} Setting empty self.neighbor_list due to self.safi_info is empty.'.format(self.hostname))
            return
        _list = self._get_table_row('neighbor', self.safi_info)
        if _list == False:
            return
        self.neighbor_list = _list

    def make_neighbor_info(self):
        '''
        populates neighbor_info dict()
        keyed on neighborid. Value is a dict() containing neighborid's info
        '''
        self._neighbor_info = dict()
        self.make_neighbor_list()

        if len(self.neighbor_list) == 0:
            self.log.warning('{} setting empty self.neighbor_info. self.neighbor_list is empty'.format(self.hostname))
            return
        for _neighbor_dict in self.neighbor_list:
            if 'neighborid' not in _neighbor_dict:
                self.log.warning('{} skipping. [neighborid] not found in _neighbor_dict {}'.format(self.hostname, _neighbor_dict))
                continue
            _neighbor = _neighbor_dict['neighborid']
            self._neighbor_info[_neighbor] = _neighbor_dict
        if len(self._neighbor_info) == 0:
            self.log.warning('{} self.neighbor_info dict is empty'.format(self.hostname))

    @property
    def vrf(self):
        return self._vrf
    @vrf.setter
    def vrf(self,_x):
        self._vrf = _x

    @property
    def neighbor(self):
        return self._neighbor
    @neighbor.setter
    def neighbor(self,_x):
        self._neighbor= _x

    #----------------------------------------------------------------------
    # vrf_info and its convenience properties
    #----------------------------------------------------------------------
    @property
    def vrf_info(self):
        '''
        Assuming refresh() was successful, vrf_info contains the same information
        as the group of convenience properties for self.vrf_info below.
        '''
        return self._vrf_info
    @property
    def vrf_name_out(self):
        try:
            return self.vrf_info['vrf-name-out']
        except:
            return 'na'
    @property
    def vrf_router_id(self):
        try:
            return self.vrf_info['vrf-router-id']
        except:
            return 'na'
    @property
    def vrf_local_as(self):
        try:
            return self.vrf_info['vrf-local-as']
        except:
            return 'na'

    #----------------------------------------------------------------------
    # afi_info and its convenience properties
    #----------------------------------------------------------------------
    @property
    def afi_info(self):
        '''
        Assuming refresh() was successful, afi_info contains the same information
        as the group of convenience properties for self.afi_info below.
        '''
        return self._afi_info
    @property
    def af_id(self):
        try:
            return self.afi_info['af-id']
        except:
            return 'na'

    #----------------------------------------------------------------------
    # safi_info and its convenience properties
    #----------------------------------------------------------------------
    @property
    def safi_info(self):
        '''
        Assuming refresh() was successful, safi_info contains information from TABLE_saf
        Else, safi_info will be an empty dict()
        '''
        return self._safi_info

    @property
    def af_name(self):
        try:
            return self.safi_info['af-name']
        except:
            return 'na'
    @property
    def bytesattrs(self):
        try:
            return self.safi_info['bytesattrs']
        except:
            return 'na'
    @property
    def bytesclusterlist(self):
        try:
            return self.safi_info['bytesclusterlist']
        except:
            return 'na'
    @property
    def bytescommunities(self):
        try:
            return self.safi_info['bytescommunities']
        except:
            return 'na'
    @property
    def bytespaths(self):
        try:
            return self.safi_info['bytespaths']
        except:
            return 'na'
    @property
    def capablepeers(self):
        try:
            return self.safi_info['capablepeers']
        except:
            return 'na'
    @property
    def configuredpeers(self):
        try:
            return self.safi_info['configuredpeers']
        except:
            return 'na'
    @property
    def dampening(self):
        try:
            return self.safi_info['dampening']
        except:
            return 'na'
    @property
    def memoryused(self):
        try:
            return self.safi_info['memoryused']
        except:
            return 'na'
    @property
    def numberattrs(self):
        try:
            return self.safi_info['numberattrs']
        except:
            return 'na'
    @property
    def numberclusterlist(self):
        try:
            return self.safi_info['numberclusterlist']
        except:
            return 'na'
    @property
    def numbercommunities(self):
        try:
            return self.safi_info['numbercommunities']
        except:
            return 'na'
    @property
    def numberpaths(self):
        try:
            return self.safi_info['numberpaths']
        except:
            return 'na'
    @property
    def tableversion(self):
        try:
            return self.safi_info['tableversion']
        except:
            return 'na'
    @property
    def totalnetworks(self):
        try:
            return self.safi_info['totalnetworks']
        except:
            return 'na'
    @property
    def totalpaths(self):
        try:
            return self.safi_info['totalpaths']
        except:
            return 'na'
    @property
    def safi(self):
        try:
            return self.safi_info['safi']
        except:
            return 'na'

    #----------------------------------------------------------------------
    # neighbor_info and its convenience properties
    #----------------------------------------------------------------------
    @property
    def neighbor_info(self):
        '''
        Assuming refresh() was successful, neighbor_info contains the same information
        as the group of convenience properties for self.neighbor_info below.
        '''
        return self._neighbor_info

    @property
    def neighborid(self):
        try:
            return self.neighbor_info[self.neighbor]['neighborid']
        except:
            return 'na'
    @property
    def neighborversion(self):
        try:
            return self.neighbor_info[self.neighbor]['neighborversion']
        except:
            return 'na'
    @property
    def msgrecvd(self):
        try:
            return self.neighbor_info[self.neighbor]['msgrecvd']
        except:
            return 'na'
    @property
    def msgsent(self):
        try:
            return self.neighbor_info[self.neighbor]['msgsent']
        except:
            return 'na'
    @property
    def neighbortableversion(self):
        try:
            return self.neighbor_info[self.neighbor]['neighbortableversion']
        except:
            return 'na'
    @property
    def inq(self):
        try:
            return self.neighbor_info[self.neighbor]['inq']
        except:
            return 'na'
    @property
    def outq(self):
        try:
            return self.neighbor_info[self.neighbor]['outq']
        except:
            return 'na'
    @property
    def neighboras(self):
        try:
            return self.neighbor_info[self.neighbor]['neighboras']
        except:
            return 'na'
    @property
    def time(self):
        try:
            return self.neighbor_info[self.neighbor]['time']
        except:
            return 'na'
    @property
    def state(self):
        try:
            return self.neighbor_info[self.neighbor]['state']
        except:
            return 'na'
    @property
    def prefixreceived(self):
        try:
            return self.neighbor_info[self.neighbor]['prefixreceived']
        except:
            return 'na'

