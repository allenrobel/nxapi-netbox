'''
Name: nxapi_vpc.py
Author: Allen Robel (arobel@cisco.com)
Description: methods which collect/return information about vpc status
'''
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

our_version = 100

class NxapiVpcStatus(NxapiBase):
    '''
        This class creates info_dict which contains the output of show vpc

        If info_dict is empty due to this library encountering an error, self.error_reason
        will be populated with the reason for the error and self.error dict will contain
        self.error['error'] = self.error_reason

        switch# sh vpc | json-pretty
        {
            "vpc-domain-id": "1", 
            "vpc-peer-status": "peer-link-down", 
            "vpc-peer-status-reason": "SYSERR_MCECM_PEER_UNRCH", 
            "vpc-peer-keepalive-status": "peer-alive", 
            "vpc-peer-consistency": "consistent", 
            "vpc-per-vlan-peer-consistency": "consistent", 
            "vpc-peer-consistency-status": "SUCCESS", 
            "vpc-type-2-consistency": "consistent", 
            "vpc-type-2-consistency-status": "SUCCESS", 
            "vpc-role": "secondary-primary", 
            "num-of-vpcs": "1", 
            "peer-gateway": "1", 
            "dual-active-excluded-vlans": "-", 
            "vpc-graceful-consistency-check-status": "enabled", 
            "vpc-auto-recovery-status": "Disabled", 
            "vpc-delay-restore-status": "Timer is off.(timeout = 400s)", 
            "vpc-delay-restore-svi-status": "Timer is off.(timeout = 100s)", 
            "operational-l3-peer": "Disabled", 
            "virtual-peerlink": "Disabled", 
            "vpc-peer-link-hdr": "Start of VPC peer-link table", 
            "TABLE_peerlink": {
                "ROW_peerlink": {
                    "peer-link-id": "1", 
                    "peerlink-ifindex": "Po1", 
                    "peer-link-port-state": "0", 
                    "peer-up-vlan-bitset": "-"
                }
            }, 
            "vpc-end": [
                "End of table", 
                "End of table"
            ], 
            "vpc-hdr": "Start of vPC table", 
            "vpc-not-es": "vPC complex", 
            "TABLE_vpc": {
                "ROW_vpc": {
                    "vpc-id": "10", 
                    "vpc-ifindex": "Po10", 
                    "vpc-port-state": "1", 
                    "phy-port-if-removed": "disabled", 
                    "vpc-thru-peerlink": "0", 
                    "vpc-consistency": "consistent", 
                    "vpc-consistency-status": "SUCCESS", 
                    "up-vlan-bitset": "1-129,3967", 
                    "es-attr": "DF: Invalid"
                }
            }
        }

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.error = dict()
        self._error_reason = None
        self.lib_version = our_version
        self.class_name = 'NxapiVpcStatus'
        self.timeout = 20
        self.na = 'na'

    @property
    def auto_recovery_status(self):
        try:
            return self.info['vpc-auto-recovery-status']
        except:
            return self.na

    @property
    def delay_restore_status(self):
        try:
            return self.info['vpc-delay-restore-status']
        except:
            return self.na

    @property
    def delay_restore_svi_status(self):
        try:
            return self.info['vpc-delay-restore-svi-status']
        except:
            return self.na

    @property
    def domain_id(self):
        try:
            return self.info['vpc-domain-id']
        except:
            return self.na

    @property
    def dual_active_excluded_vlans(self):
        try:
            return self.info['dual-active-excluded-vlans']
        except:
            return self.na

    @property
    def error_reason(self):
        return self._error_reason
    @error_reason.setter
    def error_reason(self, _x):
        self._error_reason = _x

    @property
    def graceful_consistency_check_status(self):
        try:
            return self.info['graceful-consistency-check-status']
        except:
            return self.na

    @property
    def num_of_vpcs(self):
        try:
            return self.info['num-of-vpcs']
        except:
            return self.na

    @property
    def operational_l3_peer(self):
        try:
            return self.info['operational-l3-peer']
        except:
            return self.na

    @property
    def peer_status(self):
        try:
            return self.info['vpc-peer-status']
        except:
            return self.na

    @property
    def peer_status_reason(self):
        try:
            return self.info['vpc-peer-status-reason']
        except:
            return self.na

    @property
    def peer_keepalive_status(self):
        try:
            return self.info['vpc-peer-keepalive-status']
        except:
            return self.na

    @property
    def peer_consistency(self):
        try:
            return self.info['vpc-peer-consistency']
        except:
            return self.na

    @property
    def peer_consistency_status(self):
        try:
            return self.info['vpc-peer-consistency-status']
        except:
            return self.na

    @property
    def peer_gateway(self):
        try:
            return self.info['peer-gateway']
        except:
            return self.na

    @property
    def per_vlan_peer_consistency(self):
        try:
            return self.info['vpc-per-vlan-peer-consistency']
        except:
            return self.na

    @property
    def role(self):
        try:
            return self.info['vpc-role']
        except:
            return self.na

    @property
    def type_2_consistency(self):
        try:
            return self.info['vpc-type-2-consistency']
        except:
            return self.na

    @property
    def type_2_consistency_status(self):
        try:
            return self.info['vpc-type-2-consistency-status']
        except:
            return self.na

    @property
    def virtual_peerlink(self):
        try:
            return self.info['virtual-peerlink']
        except:
            return self.na

    @property
    def peer_link_hdr(self):
        try:
            return self.info['vpc-peer-link-hdr']
        except:
            return self.na

    def make_info_dict_error(self):
        self.log.debug(self.error_reason)
        self.error = dict()
        self.error['error'] = self.error_reason
        self.info = [self.error]

    def make_peer_link_dict_error(self):
        self.log.debug(self.error_reason)
        self.error = dict()
        self.error['error'] = self.error_reason
        self.peer_link = [self.error]

    def make_vpc_dict_error(self):
        self.log.debug(self.error_reason)
        self.error = dict()
        self.error['error'] = self.error_reason
        self.vpc = [self.error]

    def make_info_dict(self):
        '''
        from self.body[0] populate self.info
        '''
        self.info = dict()
        self.error = dict()
        self.error_reason = None

        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        try:
            self.info = self.body[0]
        except:
            self.log.error('{} early return. self.info {}'.format(self.hostname, self.info))
            self.error_reason = '{} is feature vpc enabled?'.format(self.hostname)
            self.make_info_dict_error()
            return

    def make_peer_link_dict(self):
        '''
        from self.info populate self.peer_link
        '''
        try:
            self.peer_link = self._convert_to_list(self.info['TABLE_peerlink']['ROW_peerlink'])
        except:
            self.log.error('{} early return. self.info {}'.format(self.hostname, self.info))
            self.error_reason = '{} is feature vpc enabled and a vpc peer link configured?'.format(self.hostname)
            self.make_peer_link_dict_error()
            return

    def make_vpc_dict(self):
        '''
        from self.info populate self.vpc
        '''
        try:
            self.vpc = self._convert_to_list(self.info['TABLE_vpc']['ROW_vpc'])
        except:
            self.log.error('{} early return. self.info {}'.format(self.hostname, self.info))
            self.error_reason = '{} is feature vpc enabled and at least one vpc configured?'.format(self.hostname)
            self.make_vpc_dict_error()
            return

    def print_dict(self):
        '''
        print the contents of self.info
        '''
        row_index = 0
        for row in self.info:
            self.log.debug('{} self.info[{}] = {}'.format(self.hostname, row_index, self.info[row_index]))
            row_index += 1

    def refresh(self):
        self.cli = 'show vpc'
        self.show()
        self.make_info_dict()
        self.make_peer_link_dict()
        self.make_vpc_dict()

    
