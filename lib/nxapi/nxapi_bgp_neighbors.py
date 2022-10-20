#!/usr/bin/env python3
'''
Name: nxapi_bgp_neighbors.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving bgp ipv4/ipv6 unicast neighbor information 

NOTES:
    1. All timer values retrived via the properties (e.g. 00:01:00, 1d4h, 2w5d)
       are converted to float() representing seconds, e.g. 142.0
    2. Timer values in the dictionaries are in native format

TODO:
    - NxapiBgpNeighbors() verify vrf @property

'''
our_version = 117

# standard libraries
# local libraries
from nxapi.nxapi_base import NxapiBase

class NxapiBgpNeighbors(NxapiBase):
    '''
    classes which return the data within the JSON below

    All dict() are keyed on "neighbor" (ipv4) or "ipv4neighbor" (ipv6)

    - self._peers_global contains the top-level per-neighbor info
        i.e. everything within [TABLE_neighbor][ROW_neighbor] that is not in a TABLE_
        This can be retrieved with the @property self.peers_global

    - self._peers_dict contains ALL per-neighbor info
        i.e. everything within [TABLE_neighbor][ROW_neighbor], including all sub-tables
        This can be retrieved with the @property self.peers

    - self._nh_af_peer_dict contains per-neighbor info (if any) within [TABLE_capextendednhaf][ROW_capextendednhaf]
        This can be retrieved with the @property self.capextendednhaf

    - self._nh_saf_peer_dict contains per-neighbor info (if any) within [TABLE_capextendednhsaf][ROW_capextendednhsaf]
        This can be retrieved with the @property self.capextendednhsaf

    {
        "TABLE_neighbor": {
            "ROW_neighbor": [
                {
                    "neighbor": "172.18.1.4", 
                    "remoteas": "45001", 
                    "link": "ibgp", 
                    "index": "3", 
                    "inherit-template": "IBGP_PEERS", 
                    "version": "4", 
                    "remote-id": "172.18.1.4", 
                    "state": "Established", 
                    "up": "true", 
                    "elapsedtime": "PT34M9S", 
                    "sourceif": "loopback0", 
                    "ttlsecurity": "false", 
                    "passiveonly": "false", 
                    "localas-inactive": "false", 
                    "remove-privateas": "false", 
                    "lastread": "PT40S", 
                    "holdtime": "180", 
                    "keepalivetime": "60", 
                    "lastwrite": "PT40S", 
                    "keepalive": "00:00:19", 
                    "msgrecvd": "328", 
                    "notificationsrcvd": "0", 
                    "recvbufbytesinq": "0", 
                    "msgsent": "38", 
                    "notificationssent": "0", 
                    "sentbytesoutstanding": "0", 
                    "sentbytespacked": "0", 
                    "connsestablished": "1", 
                    "connsdropped": "0", 
                    "resetreason": "No error", 
                    "peerresetreason": "No error", 
                    "capsnegotiated": "false", 
                    "capmpadvertised": "true", 
                    "caprefreshadvertised": "true", 
                    "capgrdynamicadvertised": "true", 
                    "capmprecvd": "true", 
                    "caprefreshrecvd": "true", 
                    "capgrdynamicrecvd": "true", 
                    "capolddynamicadvertised": "true", 
                    "capolddynamicrecvd": "true", 
                    "caprradvertised": "true", 
                    "caprrrecvd": "true", 
                    "capoldrradvertised": "true", 
                    "capoldrrrecvd": "true", 
                    "capas4advertised": "true", 
                    "capas4recvd": "true", 
                    "TABLE_af": {
                        "ROW_af": {
                            "af-afi": "1", 
                            "TABLE_saf": {
                                "ROW_saf": {
                                    "af-safi": "1", 
                                    "af-advertised": "true", 
                                    "af-recvd": "true", 
                                    "af-name": "IPv4 Unicast"
                                }
                            }
                        }
                    }, 
                    "capgradvertised": "true", 
                    "capgrrecvd": "true", 
                    "TABLE_graf": {
                        "ROW_graf": {
                            "gr-afi": "1", 
                            "TABLE_grsaf": {
                                "ROW_grsaf": {
                                    "gr-safi": "1", 
                                    "gr-af-name": "IPv4 Unicast", 
                                    "gr-adv": "true", 
                                    "gr-recv": "true", 
                                    "gr-fwd": "false"
                                }
                            }
                        }
                    }, 
                    "grrestarttime": "120", 
                    "grstaletime": "300", 
                    "grrecvdrestarttime": "120", 
                    "TABLE_addpathscapaf": {
                        "ROW_addpathscapaf": {
                            "addpathscap-afi": "1", 
                            "TABLE_addpathscapsaf": {
                                "ROW_addpathscapsaf": {
                                    "addpathscap-safi": "1", 
                                    "addpathscap-af-name": "IPv4 Unicast", 
                                    "addpathssendcap-adv": "true", 
                                    "addpathsrecvcap-adv": "true", 
                                    "addpathssendcap-recv": "true", 
                                    "addpathsrecvcap-recv": "true"
                                }
                            }
                        }
                    }, 
                    "capaddpathsadvertised": "true", 
                    "capaddpathsrecvd": "true", 
                    "capextendednhadvertised": "true", 
                    "capextendednhrecvd": "true", 
                    "TABLE_capextendednhaf": {
                        "ROW_capextendednhaf": {
                            "capextendednh-afi": "1", 
                            "TABLE_capextendednhsaf": {
                                "ROW_capextendednhsaf": {
                                    "capextendednh-safi": "1", 
                                    "capextendednh-af-name": "IPv4 Unicast"
                                }
                            }
                        }
                    }, 
                    "epe": "false", 
                    "firstkeepalive": "false", 
                    "openssent": "1", 
                    "opensrecvd": "1", 
                    "updatessent": "290", 
                    "updatesrecvd": "292", 
                    "keepalivesent": "33", 
                    "keepaliverecvd": "33", 
                    "rtrefreshsent": "0", 
                    "rtrefreshrecvd": "0", 
                    "capabilitiessent": "2", 
                    "capabilitiesrecvd": "2", 
                    "bytessent": "889859", 
                    "bytesrecvd": "890082", 
                    "TABLE_peraf": {
                        "ROW_peraf": {
                            "per-afi": "1", 
                            "TABLE_persaf": {
                                "ROW_persaf": {
                                    "per-safi": "1", 
                                    "per-af-name": "IPv4 Unicast", 
                                    "tableversion": "195137", 
                                    "neighbortableversion": "195137", 
                                    "pfxrecvd": "24009", 
                                    "pathsrecvd": "24009", 
                                    "pfxbytes": "5185944", 
                                    "pfxsent": "24009", 
                                    "pathssent": "24009", 
                                    "insoftreconfigallowed": "false", 
                                    "sendcommunity": "true", 
                                    "sendextcommunity": "true", 
                                    "localnexthop": "172.18.1.3", 
                                    "thirdpartynexthop": "false", 
                                    "asoverride": "false", 
                                    "peerascheckdisabled": "false", 
                                    "TABLE_outpolicy": {
                                        "ROW_outpolicy": {
                                            "outpolicynr": "2", 
                                            "outpolicytype": "route-map", 
                                            "outpolicyname": "deny-anycast-net8", 
                                            "outpolicyhandle": "true"
                                        }
                                    }, 
                                    "rrconfigured": "false", 
                                    "defaultoriginate": "false", 
                                    "lasteorrecvtime": "PT38M43S", 
                                    "lasteorsenttime": "PT38M43S", 
                                    "firstconvgtime": "PT38M43S", 
                                    "pfxsentfirsteor": "4528"
                                }
                            }
                        }
                    }, 
                    "localaddr": "172.18.1.3", 
                    "localport": "20791", 
                    "remoteaddr": "172.18.1.4", 
                    "remoteport": "179", 
                    "fd": "72"
                },
            }
        }
    }

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._peers_dict = dict()
        self._peer_global = dict()

    def refresh(self):
        self.show(self.cli)
        self.make_peers_dict()
        self.make_peer_global_dict() # order important here. make_peer_global_dict() is first...
        self.make_per_peer_capextendednh_dicts() # ... make_per_peer_capextendednh_dicts() is second as we need peer state info in make_per_peer_capextendednh_dicts()

        for _peer in self.peer_global:
            self.log.debug('{} peer {} peer_global {}'.format(self.hostname, _peer, self.peer_global[_peer]))
        for _peer in self._nh_af_peer_dict:
            self.log.debug('{} peer {} capextendednhaf {}'.format(self.hostname, _peer, self._nh_af_peer_dict[_peer]))
        for _peer in self._nh_saf_peer_dict:
            self.log.debug('{} peer {} capextendednhsaf {}'.format(self.hostname, _peer, self._nh_saf_peer_dict[_peer]))

    def make_per_peer_capextendednh_dicts(self):
        '''
        NXOS: version 7.0(3)I4(7)

        "TABLE_capextendednhaf": {
            "ROW_capextendednhaf": {
                "capextendednh-afi": "1", 
                "TABLE_capextendednhsaf": {
                    "ROW_capextendednhsaf": {
                        "capextendednh-safi": "1", 
                        "capextendednh-af-name": [
                            "IPv4 Unicast", 
                            "1", 
                            "2001:232::80"
                        ]
                    }
                }
            }
        }, 


        NXOS: version 7.0(3)I6(1), 7.0(3)I7(3), 9.2(1)

        'TABLE_capextendednhaf': {
            'ROW_capextendednhaf': {
                'capextendednh-afi': '1', 
                'TABLE_capextendednhsaf': {  <--
                    'ROW_capextendednhsaf': {
                        'capextendednh-safi': '1', 
                        'capextendednh-af-name': 'IPv4 Unicast'
                    }
                }
            }
        }
        '''
        def __fix_ipv6_nh_af_name(_saf_value):
            '''
            For older images, ipv6 address is returned for capextendednh-af-name
            we handle this by testing to see if af-name is an ipv6 address and, if so, change 
            the value to 'IPv6 Unicast', which is what more recent images return
            '''
            if _saf_value in ['IPv4 Unicast', 'VPNv4 Unicast', 'IPv6 Unicast']:
                # If the saf_value is legit, return immediately to avoid error logs from is_ipv6_address
                return
            if self.verify.is_ipv6_address(_saf_value):
                self.log.debug('{} older image. {} is ipv6 address {}, change value to IPv6 Unicast'.format(
                    self.hostname,
                    _saf_key,
                    _saf_value))
                return 'IPv6 Unicast'
            return _saf_value

        # temporary dicts which are copied to self._nh_* if successfully populated
        _nh_af_peer_dict = dict()
        _nh_saf_peer_dict = dict()
        # final dicts which receive the info from temporary dicts, if they are successfully populated
        self._nh_af_peer_dict = dict()
        self._nh_saf_peer_dict = dict()
        for _peer in self._peers_dict:
            _nh_af_peer_dict[_peer] = dict()
            _nh_saf_peer_dict[_peer] = dict()
            self._nh_af_peer_dict[_peer] = dict()
            self._nh_saf_peer_dict[_peer] = dict()

            _row_capextended_nh_af = self._get_table_row('capextendednhaf', self._peers_dict[_peer])
            if _row_capextended_nh_af == False:
                self.log.debug('{} skipping peer {}.'.format(self.hostname, _peer))
                continue

            for _capextended_nh_af_dict in _row_capextended_nh_af:
                if 'capextendednh-afi' not in _capextended_nh_af_dict:
                    self.log.debug('{} early return: key [capextendednh-afi] not found in _capextended_nh_af_dict {}'.format(self.hostname, _capextended_nh_af_dict))
                    return
                for _key in _capextended_nh_af_dict:
                    if _key == 'capextendednh-afi':
                        _afi = _capextended_nh_af_dict[_key]
                        _nh_saf_peer_dict[_peer][_afi] = dict()
                        _nh_af_peer_dict[_peer][_key] = _afi
                        continue

                    _row_capextended_nh_saf = self._get_table_row('capextendednhsaf', _capextended_nh_af_dict)
                    if _row_capextended_nh_af == False:
                        continue

                    for _saf_dict in _row_capextended_nh_saf:
                        for _saf_key in _saf_dict:
                            _saf_value = _saf_dict[_saf_key]
                            if _saf_key == 'capextendednh-af-name':
                                _saf_value = __fix_ipv6_nh_af_name(_saf_value)
                            _nh_saf_peer_dict[_peer][_afi][_saf_key] = _saf_value

            self._nh_af_peer_dict[_peer] = _nh_af_peer_dict[_peer]
            self._nh_saf_peer_dict[_peer] = _nh_saf_peer_dict[_peer]


    def make_peers_dict(self):
        '''
        creates dictionary keyed on peer ipv4/ipv6 address
        values are dict() containing per-peer info
        '''
        self._peers_dict = dict()
        if not self._verify_body_length():
            return
        _list = self._get_table_row('neighbor', self.body[0])
        if _list == False:
            return
        for _dict in _list:
            if self.peer_dict_key not in _dict:
                self.log.debug('{} skipping. key [{}] not in _dict {}'.format(self.hostname, self.peer_dict_key, _dict))
                continue
            self._peers_dict[_dict[self.peer_dict_key]] = _dict

    def make_peer_global_dict(self):
        self._peer_global_dict = dict()
        for _peer in self._peers_dict:
            self.log.debug('{} peer -> {}'.format(self.hostname, _peer))
            self._peer_global_dict[_peer] = dict()
            for _key in self._peers_dict[_peer]:
                if 'TABLE_' in _key:
                    continue
                self.log.debug('{} key {} value {}'.format(self.hostname, _key, self._peers_dict[_peer][_key]))
                self._peer_global_dict[_peer][_key] = self._peers_dict[_peer][_key]

    # dict @properties
    # these return dictionaries created by NxapiBgpNeighbors()
    @property
    def peers(self):
        return self._peers_dict

    @property
    def peer_global(self):
        return self._peer_global_dict

    @property
    def capextendednhaf(self):
        return self._nh_af_peer_dict

    @property
    def capextendednhsaf(self):
        return self._nh_saf_peer_dict

    # VRF @properties (TODO, verify this)

    @property
    def vrf_name_out(self):
        try:
            return self._vrf_dict['vrf-name-out']
        except:
            return 'na'



    # properties returning items from capextendednh table
    @property
    def capextendednh_afi(self):
        try:
            return self._nh_af_peer_dict[self.peer]['capextendednh-afi']
        except:
            return 'na'

    @property
    def capextendednh_af_name(self):
        try:
            return self._nh_saf_peer_dict[self.peer][self.capextendednh_afi]['capextendednh-af-name']
        except:
            return 'na'

    @property
    def capextendednh_safi(self):
        try:
            return self._nh_saf_peer_dict[self.peer][self.capextendednh_afi]['capextendednh-safi']
        except:
            return 'na'


    # per-peer global @properties

    @property
    def bfd(self):
        try:
            return self._peers_dict[self.peer]['bfd']
        except:
            return 'na'

    @property
    def bytesrecvd(self):
        try:
            return self._peers_dict[self.peer]['bytesrecvd']
        except:
            return 'na'

    @property
    def bytessent(self):
        try:
            return self._peers_dict[self.peer]['bytessent']
        except:
            return 'na'

    @property
    def capabilitiesrecvd(self):
        try:
            return self._peers_dict[self.peer]['capabilitiesrecvd']
        except:
            return 'na'

    @property
    def capabilitiessent(self):
        try:
            return self._peers_dict[self.peer]['capabilitiessent']
        except:
            return 'na'

    @property
    def capas4advertised(self):
        try:
            return self._peers_dict[self.peer]['capas4advertised']
        except:
            return 'na'

    @property
    def capas4recvd(self):
        try:
            return self._peers_dict[self.peer]['capas4recvd']
        except:
            return 'na'

    @property
    def capextendednhadvertised(self):
        try:
            return self._peers_dict[self.peer]['capextendednhadvertised']
        except:
            return 'na'

    @property
    def capextendednhrecvd(self):
        try:
            return self._peers_dict[self.peer]['capextendednhrecvd']
        except:
            return 'na'

    @property
    def capgradvertised(self):
        try:
            return self._peers_dict[self.peer]['capgradvertised']
        except:
            return 'na'

    @property
    def capgrdynamicadvertised(self):
        try:
            return self._peers_dict[self.peer]['capgrdynamicadvertised']
        except:
            return 'na'

    @property
    def capgrdynamicrecvd(self):
        try:
            return self._peers_dict[self.peer]['capgrdynamicrecvd']
        except:
            return 'na'

    @property
    def capgrrecvd(self):
        try:
            return self._peers_dict[self.peer]['capgrrecvd']
        except:
            return 'na'

    @property
    def capmpadvertised(self):
        try:
            return self._peers_dict[self.peer]['capmpadvertised']
        except:
            return 'na'

    @property
    def capmprecvd(self):
        try:
            return self._peers_dict[self.peer]['capmprecvd']
        except:
            return 'na'

    @property
    def capolddynamicadvertised(self):
        try:
            return self._peers_dict[self.peer]['capolddynamicadvertised']
        except:
            return 'na'

    @property
    def capolddynamicrecvd(self):
        try:
            return self._peers_dict[self.peer]['capolddynamicrecvd']
        except:
            return 'na'

    @property
    def capoldrradvertised(self):
        try:
            return self._peers_dict[self.peer]['capoldrradvertised']
        except:
            return 'na'

    @property
    def capoldrrrecvd(self):
        try:
            return self._peers_dict[self.peer]['capoldrrrecvd']
        except:
            return 'na'

    @property
    def caprefreshadvertised(self):
        try:
            return self._peers_dict[self.peer]['caprefreshadvertised']
        except:
            return 'na'

    @property
    def caprefreshrecvd(self):
        try:
            return self._peers_dict[self.peer]['caprefreshrecvd']
        except:
            return 'na'

    @property
    def caprradvertised(self):
        try:
            return self._peers_dict[self.peer]['caprradvertised']
        except:
            return 'na'

    @property
    def caprrrecvd(self):
        try:
            return self._peers_dict[self.peer]['caprrrecvd']
        except:
            return 'na'

    @property
    def capsnegotiated(self):
        try:
            return self._peers_dict[self.peer]['capsnegotiated']
        except:
            return 'na'

    @property
    def connectedif(self):
        try:
            return self._peers_dict[self.peer]['connectedif']
        except:
            return 'na'

    @property
    def connsdropped(self):
        try:
            return self._peers_dict[self.peer]['connsdropped']
        except:
            return 'na'

    @property
    def connsestablished(self):
        try:
            return self._peers_dict[self.peer]['connsestablished']
        except:
            return 'na'

    @property
    def elapsedtime(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['elapsedtime'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def fd(self):
        try:
            return self._peers_dict[self.peer]['fd']
        except:
            return 'na'

    @property
    def firstkeepalive(self):
        try:
            return self._peers_dict[self.peer]['firstkeepalive']
        except:
            return 'na'

    @property
    def grrecvdrestarttime(self):
        try:
            return self._peers_dict[self.peer]['grrecvdrestarttime']
        except:
            return 'na'

    @property
    def grrestarttime(self):
        try:
            return self._peers_dict[self.peer]['grrestarttime']
        except:
            return 'na'

    @property
    def grstaletime(self):
        try:
            return self._peers_dict[self.peer]['grstaletime']
        except:
            return 'na'

    @property
    def holdtime(self):
        try:
            return self._peers_dict[self.peer]['holdtime']
        except:
            return 'na'

    @property
    def index(self):
        try:
            return self._peers_dict[self.peer]['index']
        except:
            return 'na'

    @property
    def inherit_template(self):
        try:
            return self._peers_dict[self.peer]['inherit-template']
        except:
            return 'na'

    @property
    def ipv6localaddr(self):
        try:
            return self._peers_dict[self.peer]['ipv6localaddr']
        except:
            return 'na'

    @property
    def ipv6neighbor(self):
        try:
            return self._peers_dict[self.peer]['ipv6neighbor']
        except:
            return 'na'

    @property
    def ipv6remoteaddr(self):
        try:
            return self._peers_dict[self.peer]['ipv6remoteaddr']
        except:
            return 'na'

    @property
    def keepalive(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['keepalive'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def keepaliverecvd(self):
        try:
            return self._peers_dict[self.peer]['keepaliverecvd']
        except:
            return 'na'

    @property
    def keepalivesent(self):
        try:
            return self._peers_dict[self.peer]['keepalivesent']
        except:
            return 'na'

    @property
    def keepalivetime(self):
        try:
            return self._peers_dict[self.peer]['keepalivetime']
        except:
            return 'na'

    @property
    def lastread(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['lastread'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def lastwrite(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['lastwrite'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def link(self):
        try:
            return self._peers_dict[self.peer]['link']
        except:
            return 'na'

    @property
    def localas(self):
        try:
            return self._peers_dict[self.peer]['localas']
        except:
            return 'na'

    @property
    def localport(self):
        try:
            return self._peers_dict[self.peer]['localport']
        except:
            return 'na'

    @property
    def msgrecvd(self):
        try:
            return self._peers_dict[self.peer]['msgrecvd']
        except:
            return 'na'

    @property
    def msgsent(self):
        try:
            return self._peers_dict[self.peer]['msgsent']
        except:
            return 'na'

    @property
    def notificationsrcvd(self):
        try:
            return self._peers_dict[self.peer]['notificationsrcvd']
        except:
            return 'na'

    @property
    def notificationssent(self):
        try:
            return self._peers_dict[self.peer]['notificationssent']
        except:
            return 'na'

    @property
    def opensrecvd(self):
        try:
            return self._peers_dict[self.peer]['opensrecvd']
        except:
            return 'na'

    @property
    def openssent(self):
        try:
            return self._peers_dict[self.peer]['openssent']
        except:
            return 'na'

    @property
    def peerresetreason(self):
        try:
            return self._peers_dict[self.peer]['peerresetreason']
        except:
            return 'na'

    @property
    def peerresettime(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['peerresettime'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def recvbufbytes(self):
        try:
            return self._peers_dict[self.peer]['recvbufbytes']
        except:
            return 'na'

    @property
    def remote_id(self):
        try:
            return self._peers_dict[self.peer]['remote-id']
        except:
            return 'na'

    @property
    def remoteas(self):
        try:
            return self._peers_dict[self.peer]['remoteas']
        except:
            return 'na'

    @property
    def remoteport(self):
        try:
            return self._peers_dict[self.peer]['remoteport']
        except:
            return 'na'

    @property
    def remove_privateas(self):
        try:
            return self._peers_dict[self.peer]['remove-privateas']
        except:
            return 'na'

    @property
    def resetreason(self):
        try:
            return self._peers_dict[self.peer]['resetreason']
        except:
            return 'na'

    @property
    def resettime(self):
        try:
            self.nx_timer.refresh(self._peers_dict[self.peer]['resettime'])
            return self.nx_timer.timer2sec
        except:
            return 'na'

    @property
    def rtrefreshrecvd(self):
        try:
            return self._peers_dict[self.peer]['rtrefreshrecvd']
        except:
            return 'na'

    @property
    def rtrefreshsent(self):
        try:
            return self._peers_dict[self.peer]['rtrefreshsent']
        except:
            return 'na'

    @property
    def sentbytesoutstanding(self):
        try:
            return self._peers_dict[self.peer]['sentbytesoutstanding']
        except:
            return 'na'

    @property
    def sourceif(self):
        try:
            return self._peers_dict[self.peer]['sourceif']
        except:
            return 'na'

    @property
    def state(self):
        try:
            return self._peers_dict[self.peer]['state']
        except:
            return 'na'

    @property
    def up(self):
        try:
            return self._peers_dict[self.peer]['up']
        except:
            return 'na'

    @property
    def updatesrecvd(self):
        try:
            return self._peers_dict[self.peer]['updatesrecvd']
        except:
            return 'na'

    @property
    def updatessent(self):
        try:
            return self._peers_dict[self.peer]['updatessent']
        except:
            return 'na'

    @property
    def version(self):
        try:
            return self._peers_dict[self.peer]['version']
        except:
            return 'na'


class NxapiBgpNeighborsIpv4(NxapiBgpNeighbors):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.cli = 'show bgp ipv4 unicast neighbors'
        # self.peer_dict_key is necessary because NXOS labels are different for ivp4 "neighbor" and ipv6 "ipv6neighbor" :-(
        self.peer_dict_key = 'neighbor'

    @property
    def peer(self):
        return self._peer
    @peer.setter
    def peer(self, _x):
        '''
        if self.peer is set, then properties to retrieve items from within self._peers_dict will return 
        items associated with self.peer
        '''
        if not self.verify.is_ipv4_address(_x):
            self.log.debug('ignored. expected ip address with format a.b.c.d, got {}'.format(_x))
            return
        self._peer = _x

class NxapiBgpNeighborsIpv6(NxapiBgpNeighbors):
    def __init__(self, username, password, mgmt_ip, loglevel):
        super().__init__(username, password, mgmt_ip, loglevel)
        self.cli = 'show bgp ipv6 unicast neighbors'
        # self.peer_dict_key is necessary because NXOS labels are different for ivp4 "neighbor" and ipv6 "ipv6neighbor" :-(
        self.peer_dict_key = 'ipv6neighbor'

    @property
    def peer(self):
        return self._peer
    @peer.setter
    def peer(self, _x):
        '''
        if self.peer is set, then properties to retrieve items from within self._peers_dict will return 
        items associated with self.peer
        '''
        if not self.verify.is_ipv4_address(_x) and not self.verify.is_ipv6_address(_x):
            self.log.debug('ignored. expected either an ipv4 or ipv6 address')
            return
        self._peer = _x



class NxapiBgpUnicastSummary(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._vrf_dict = dict()
        self._af_dict = dict()
        self._saf_dict = dict()
        self._peers_dict = dict()

        # if the user sets this, e.g. by invoking @property self.peer = '10.1.32.1', then
        # items with self._peers_dict can be retrieved for self.peer using the
        # properties defined under the "Peer @properties" section
        self._peer = None

    def refresh(self):
        self.show(self.cli)
        self._make_vrf_dict_from_body()
        self._make_af_dict_from_vrf_dict()
        self._make_saf_dict_from_af_dict()
        self._make_peers_dict_from_saf_dict()

    def _make_vrf_dict_from_body(self):
        self._vrf_dict = dict()
        if self._verify_body_length() == False:
            return
        _list = self._get_table_row('vrf', self.body[0])
        if _list == False:
            return
        self._vrf_dict = _list[0]

    def _make_af_dict_from_vrf_dict(self):
        self._af_dict = dict()
        _list = self._get_table_row('af', self._vrf_dict)
        if _list == False:
            return
        self._af_dict = _list[0]

    def _make_saf_dict_from_af_dict(self):
        self._saf_dict = dict()
        _list = self._get_table_row('saf', self._af_dict)
        if _list == False:
            return
        self._saf_dict = _list[0]

    def _make_peers_dict_from_saf_dict(self):
        '''
        creates dict() self._peers_dict
            - keys: neighborid e.g. 10.22.0.4
            - values: dict() with the keys below
            Example access:
                peer_state = bgp.peers_dict['10.22.0.4']['state']

                {
                    "neighborid": "10.22.0.4", 
                    "neighborversion": "4", 
                    "msgrecvd": "44100", 
                    "msgsent": "44021", 
                    "neighbortableversion": "206", 
                    "inq": "0", 
                    "outq": "0", 
                    "neighboras": "65305", 
                    "time": "P2DT58M53S", 
                    "state": "Established", 
                    "prefixreceived": "14"
                }
        '''
        self._peers_dict = dict()
        _list = self._get_table_row('neighbor', self._saf_dict)
        if _list == False:
            return
        for _peer_dict in _list:
            if 'neighborid' not in _peer_dict:
                self.log.debug('{} skipping. neighborid key not in _peer_dict {}'.format(self.hostname, _peer_dict))
                continue
            self._peers_dict[_peer_dict['neighborid']] = _peer_dict


    @property
    def peers(self):
        return self._peers_dict

    # VRF @properties

    @property
    def vrf_name_out(self):
        try:
            return self._vrf_dict['vrf-name-out']
        except:
            return 'na'

    @property
    def vrf_router_id(self):
        try:
            return self._vrf_dict['vrf-router-id']
        except:
            return 'na'

    @property
    def vrf_local_as(self):
        try:
            return self._vrf_dict['vrf-local-as']
        except:
            return 'na'

    @property
    def vrf_router_id(self):
        try:
            return self._vrf_dict['vrf-router-id']
        except:
            return 'na'




    # SAFI @properties

    @property
    def safi(self):
        try:
            return self._saf_dict['safi']
        except:
            return 'na'

    @property
    def af_name(self):
        try:
            return self._saf_dict['af-name']
        except:
            return 'na'

    @property
    def tableversion(self):
        try:
            return self._saf_dict['tableversion']
        except:
            return 'na'

    @property
    def configuredpeers(self):
        try:
            return self._saf_dict['configuredpeers']
        except:
            return 'na'

    @property
    def capablepeers(self):
        try:
            return self._saf_dict['capablepeers']
        except:
            return 'na'

    @property
    def totalnetworks(self):
        try:
            return self._saf_dict['totalnetworks']
        except:
            return 'na'

    @property
    def totalpaths(self):
        try:
            return self._saf_dict['totalpaths']
        except:
            return 'na'

    @property
    def memoryused(self):
        try:
            return self._saf_dict['memoryused']
        except:
            return 'na'

    @property
    def numberattrs(self):
        try:
            return self._saf_dict['numberattrs']
        except:
            return 'na'

    @property
    def bytesattrs(self):
        try:
            return self._saf_dict['bytesattrs']
        except:
            return 'na'

    @property
    def numberpaths(self):
        try:
            return self._saf_dict['numberpaths']
        except:
            return 'na'

    @property
    def bytespaths(self):
        try:
            return self._saf_dict['bytespaths']
        except:
            return 'na'

    @property
    def numbercommunities(self):
        try:
            return self._saf_dict['numbercommunities']
        except:
            return 'na'

    @property
    def bytescommunities(self):
        try:
            return self._saf_dict['bytescommunities']
        except:
            return 'na'

    @property
    def numberclusterlist(self):
        try:
            return self._saf_dict['numberclusterlist']
        except:
            return 'na'

    @property
    def bytesclusterlist(self):
        try:
            return self._saf_dict['bytesclusterlist']
        except:
            return 'na'

    @property
    def dampening(self):
        try:
            return self._saf_dict['dampening']
        except:
            return 'na'




    # Peer @properties

    @property
    def neighborid(self):
        try:
            return self.peers[self.peer]['neighborid']
        except:
            return 'na'

    @property
    def neighborversion(self):
        try:
            return self.peers[self.peer]['neighborversion']
        except:
            return 'na'

    @property
    def msgrecvd(self):
        try:
            return self.peers[self.peer]['msgrecvd']
        except:
            return 'na'

    @property
    def msgsent(self):
        try:
            return self.peers[self.peer]['msgsent']
        except:
            return 'na'

    @property
    def neighbortableversion(self):
        try:
            return self.peers[self.peer]['neighbortableversion']
        except:
            return 'na'

    @property
    def inq(self):
        try:
            return self.peers[self.peer]['inq']
        except:
            return 'na'

    @property
    def outq(self):
        try:
            return self.peers[self.peer]['outq']
        except:
            return 'na'

    @property
    def neighboras(self):
        try:
            return self.peers[self.peer]['neighboras']
        except:
            return 'na'

    @property
    def time(self):
        try:
            return self.peers[self.peer]['time']
        except:
            return 'na'

    @property
    def state(self):
        try:
            return self.peers[self.peer]['state']
        except:
            return 'na'

    @property
    def prefixreceived(self):
        try:
            return self.peers[self.peer]['prefixreceived']
        except:
            return 'na'


class NxapiBgpUnicastSummaryIpv4(NxapiBgpUnicastSummary):
    '''
    methods and properties for retrieving information from 'show bgp ipv4 unicast summary vrf <vrf>'

    Synopsis:

    from log import get_logger
    from nxapi_bgp_neighbors import NxapiBgpUnicastSummaryIpv4

    log = get_logger('my_script_name', 'INFO', 'DEBUG')
    bgp = NxapiBgpUnicastSummaryIpv4('admin', 'mypassword', '172.22.150.33', log)
    bgp.refresh()
    log.info('capable_peers {}'.format(bgp.capablepeers))
    log.info('total_paths {}'.format(bgp.total_paths))
    log.info('vrf_name {}'.format(bgp.vrf_name_out))
    log.info('local_router_id {}'.format(bgp.vrf_router_id))

    # setting bgp.peer enables retrieval of items for that specific peer
    # property names are identical to keys in the dicts() within [TABLE_neighbor][ROW_neighbor]

    for peer in bgp.peers:
        bgp.peer = peer
        log.info('peer {} state {}'.format(peer, bgp.state))
        log.info('peer {} neighbor_as {}'.format(peer, bgp.neighboras))



    The following JSON is expected to be returned by the DUT

    switch# show bgp ipv4 unicast summary vrf default | json-pretty 
    {
        "TABLE_vrf": {
            "ROW_vrf": {
                "vrf-name-out": "default", 
                "vrf-router-id": "10.23.0.0", 
                "vrf-local-as": "65306", 
                "TABLE_af": {
                    "ROW_af": {
                        "af-id": "1", 
                        "TABLE_saf": {
                            "ROW_saf": {
                                "safi": "1", 
                                "af-name": "IPv4 Unicast", 
                                "tableversion": "206", 
                                "configuredpeers": "2", 
                                "capablepeers": "2", 
                                "totalnetworks": "26", 
                                "totalpaths": "33", 
                                "memoryused": "6588", 
                                "numberattrs": "7", 
                                "bytesattrs": "1148", 
                                "numberpaths": "4", 
                                "bytespaths": "48", 
                                "numbercommunities": "5", 
                                "bytescommunities": "184", 
                                "numberclusterlist": "0", 
                                "bytesclusterlist": "0", 
                                "dampening": "false", 
                                "TABLE_neighbor": {
                                    "ROW_neighbor": [
                                        {
                                            "neighborid": "10.22.0.0", 
                                            "neighborversion": "4", 
                                            "msgrecvd": "44129", 
                                            "msgsent": "43993", 
                                            "neighbortableversion": "206", 
                                            "inq": "0", 
                                            "outq": "0", 
                                            "neighboras": "65305", 
                                            "time": "P1DT2H14M9S", 
                                            "state": "Established", 
                                            "prefixreceived": "15"
                                        }, 
                                        {
                                            "neighborid": "10.22.0.4", 
                                            "neighborversion": "4", 
                                            "msgrecvd": "44100", 
                                            "msgsent": "44021", 
                                            "neighbortableversion": "206", 
                                            "inq": "0", 
                                            "outq": "0", 
                                            "neighboras": "65305", 
                                            "time": "P2DT58M53S", 
                                            "state": "Established", 
                                            "prefixreceived": "14"
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
    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.cli = 'show bgp ipv4 unicast summary vrf {}'.format(self.vrf)

    @property
    def peer(self):
        return self._peer
    @peer.setter
    def peer(self, _x):
        '''
        if self.peer is set, then properties to retrieve items from within self._peers_dict will return 
        items associated with self.peer
        '''
        if not self.verify.is_ipv4_address(_x):
            self.log.debug('ignored. expected ip address with format a.b.c.d')
            return
        self._peer = _x



class NxapiBgpUnicastSummaryIpv6(NxapiBgpUnicastSummary):
    '''
    methods and properties for retrieving information from 'show bgp ipv6 unicast summary vrf <vrf>'

    Synopsis:

    from log import get_logger
    from nxapi_bgp_neighbors import NxapiBgpUnicastSummaryIpv6

    log = get_logger('my_script_name', 'INFO', 'DEBUG')
    bgp = NxapiBgpUnicastSummaryIpv6('admin', 'mypassword', '172.22.150.33', log)
    bgp.refresh()
    log.info('capable_peers {}'.format(bgp.capablepeers))
    log.info('total_paths {}'.format(bgp.total_paths))
    log.info('vrf_name {}'.format(bgp.vrf_name_out))
    log.info('local_router_id {}'.format(bgp.vrf_router_id))

    # setting bgp.peer enables retrieval of items for that specific peer
    # property names are identical to keys in the dicts() within [TABLE_neighbor][ROW_neighbor]

    for peer in bgp.peers:
        bgp.peer = peer
        log.info('peer {} state {}'.format(peer, bgp.state))
        log.info('peer {} neighbor_as {}'.format(peer, bgp.neighboras))


    The following JSON is expected to be returned by the DUT

    ebay_leaf_301# show bgp ipv6 unicast summary | json-pretty
    {
        "TABLE_vrf": {
            "ROW_vrf": {
                "vrf-name-out": "default", 
                "vrf-router-id": "10.13.0.0", 
                "vrf-local-as": "65304", 
                "TABLE_af": {
                    "ROW_af": {
                        "af-id": "2", 
                        "TABLE_saf": {
                            "ROW_saf": {
                                "safi": "1", 
                                "af-name": "IPv6 Unicast", 
                                "tableversion": "67", 
                                "configuredpeers": "2", 
                                "capablepeers": "2", 
                                "totalnetworks": "60", 
                                "totalpaths": "65", 
                                "memoryused": "14540", 
                                "numberattrs": "7", 
                                "bytesattrs": "1148", 
                                "numberpaths": "4", 
                                "bytespaths": "48", 
                                "numbercommunities": "5", 
                                "bytescommunities": "184", 
                                "numberclusterlist": "0", 
                                "bytesclusterlist": "0", 
                                "dampening": "false", 
                                "TABLE_neighbor": {
                                    "ROW_neighbor": [
                                        {
                                            "neighborid": "10.12.0.0", 
                                            "neighborversion": "4", 
                                            "msgrecvd": "19066", 
                                            "msgsent": "19008", 
                                            "neighbortableversion": "67", 
                                            "inq": "0", 
                                            "outq": "0", 
                                            "neighboras": "65303", 
                                            "time": "PT21H8M30S", 
                                            "state": "Established", 
                                            "prefixreceived": "31"
                                        }, 
                                        {
                                            "neighborid": "10.12.0.8", 
                                            "neighborversion": "4", 
                                            "msgrecvd": "19065", 
                                            "msgsent": "19006", 
                                            "neighbortableversion": "67", 
                                            "inq": "0", 
                                            "outq": "0", 
                                            "neighboras": "65303", 
                                            "time": "PT21H8M39S", 
                                            "state": "Established", 
                                            "prefixreceived": "30"
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

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.cli = 'show bgp ipv6 unicast summary vrf {}'.format(self.vrf)

    @property
    def peer(self):
        return self._peer
    @peer.setter
    def peer(self, _x):
        '''
        if self.peer is set, then properties to retrieve items from within self._peers_dict will return 
        items associated with self.peer
        '''
        if not self.verify.is_ipv4_address(_x) and not self.verify.is_ipv6_address(_x):
            self.log.debug('ignored. expected either an ipv4 or ipv6 address')
            return
        self._peer = _x


