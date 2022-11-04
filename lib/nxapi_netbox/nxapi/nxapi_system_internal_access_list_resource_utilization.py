#!/usr/bin/env python3
our_version = 112
'''
Name: nxapi_system_internal_access_list_resource_utilization.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes for retrieving acl tcam utilization via NXAPI 
'''

# standard libraries
# local libraries
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

class NxapiAccessList(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._instance_dict = dict()
        self._module = None
        self._feature = None

        # Map the DUT's JSON keys to the script's output titles
        # e.g. JSON key 'Copp IPv4+Mac' maps to script title copp_ipv4_mac
        self.hdr_to_key = dict()
        self.hdr_to_key['Copp IPv4+Mac'] = 'copp_ipv4_mac'
        self.hdr_to_key['Copp IPv6+Mac'] = 'copp_ipv6_mac'
        self.hdr_to_key['Egress Dest info table'] = 'egress_dest_info_table'
        # TOR
        self.hdr_to_key['Egress RACL'] = 'egress_racl'
        self.hdr_to_key['Egress RACL MAC'] = 'egress_racl_mac'
        self.hdr_to_key['Egress RACL IPv4'] = 'egress_racl_ipv4'
        self.hdr_to_key['Egress RACL IPv6'] = 'egress_racl_ipv6'
        self.hdr_to_key['Egress RACL ALL'] = 'egress_racl_all'
        self.hdr_to_key['Egress RACL OTHER'] = 'egress_racl_other'

        self.hdr_to_key['Egress SUP'] = 'egress_sup'
        self.hdr_to_key['Egress SUP IPv4'] = 'egress_sup_ipv4'
        self.hdr_to_key['Egress SUP IPv6'] = 'egress_sup_ipv6'
        self.hdr_to_key['Egress SUP MAC'] = 'egress_sup_mac'
        self.hdr_to_key['Egress SUP ALL'] = 'egress_sup_all'
        self.hdr_to_key['Egress SUP OTHER'] = 'egress_sup_other'

        self.hdr_to_key['Ingress RACL'] = 'ingress_racl'
        self.hdr_to_key['Ingress RACL MAC'] = 'ingress_racl_mac'
        self.hdr_to_key['Ingress RACL IPv4'] = 'ingress_racl_ipv4'
        self.hdr_to_key['Ingress RACL IPv6'] = 'ingress_racl_ipv6'
        self.hdr_to_key['Ingress RACL ALL'] = 'ingress_racl_all'
        self.hdr_to_key['Ingress RACL OTHER'] = 'ingress_racl_other'

        self.hdr_to_key['Ingress L2 QOS'] = 'ingress_l2_qos'
        self.hdr_to_key['Ingress L2 QOS MAC'] = 'ingress_l2_qos_mac'
        self.hdr_to_key['Ingress L2 QOS IPv4'] = 'ingress_l2_qos_ipv4'
        self.hdr_to_key['Ingress L2 QOS IPv6'] = 'ingress_l2_qos_ipv6'
        self.hdr_to_key['Ingress L2 QOS ALL'] = 'ingress_l2_qos_all'
        self.hdr_to_key['Ingress L2 QOS OTHER'] = 'ingress_l2_qos_other'

        self.hdr_to_key['Ingress L2 SPAN ACL'] = 'ingress_l2_span_acl'
        self.hdr_to_key['Ingress L2 SPAN ACL MAC'] = 'ingress_l2_span_acl_mac'
        self.hdr_to_key['Ingress L2 SPAN ACL IPv4'] = 'ingress_l2_span_acl_ipv4'
        self.hdr_to_key['Ingress L2 SPAN ACL IPv6'] = 'ingress_l2_span_acl_ipv6'
        self.hdr_to_key['Ingress L2 SPAN ACL ALL'] = 'ingress_l2_span_acl_all'
        self.hdr_to_key['Ingress L2 SPAN ACL OTHER'] = 'ingress_l2_span_acl_other'

        self.hdr_to_key['Ingress L3/VLAN QOS'] = 'ingress_l3_vlan_qos'
        self.hdr_to_key['Ingress L3/VLAN QOS MAC'] = 'ingress_l3_vlan_qos_mac'
        self.hdr_to_key['Ingress L3/VLAN QOS IPv4'] = 'ingress_l3_vlan_qos_ipv4'
        self.hdr_to_key['Ingress L3/VLAN QOS IPv6'] = 'ingress_l3_vlan_qos_ipv6'
        self.hdr_to_key['Ingress L3/VLAN QOS ALL'] = 'ingress_l3_vlan_qos_all'
        self.hdr_to_key['Ingress L3/VLAN QOS OTHER'] = 'ingress_l3_vlan_qos_other'

        self.hdr_to_key['Ingress L3/VLAN SPAN ACL'] = 'ingress_l3_vlan_span_acl'
        self.hdr_to_key['Ingress L3/VLAN SPAN ACL MAC'] = 'ingress_l3_vlan_span_acl_mac'
        self.hdr_to_key['Ingress L3/VLAN SPAN ACL IPv4'] = 'ingress_l3_vlan_span_acl_ipv4'
        self.hdr_to_key['Ingress L3/VLAN SPAN ACL IPv6'] = 'ingress_l3_vlan_span_acl_ipv6'
        self.hdr_to_key['Ingress L3/VLAN SPAN ACL ALL'] = 'ingress_l3_vlan_span_acl_all'
        self.hdr_to_key['Ingress L3/VLAN SPAN ACL OTHER'] = 'ingress_l3_vlan_span_acl_other'

        self.hdr_to_key['Feature ARP SNOOP'] = 'feature_arp_snoop'
        self.hdr_to_key['Feature ARP SNOOP MAC'] = 'feature_arp_snoop_mac'
        self.hdr_to_key['Feature ARP SNOOP IPv4'] = 'feature_arp_snoop_ipv4'
        self.hdr_to_key['Feature ARP SNOOP IPv6'] = 'feature_arp_snoop_ipv6'
        self.hdr_to_key['Feature ARP SNOOP ALL'] = 'feature_arp_snoop_all'
        self.hdr_to_key['Feature ARP SNOOP OTHER'] = 'feature_arp_snoop_other'

        self.hdr_to_key['Feature BFD'] = 'feature_bfd'
        self.hdr_to_key['Feature BFD IPv4'] = 'feature_bfd_ipv4'
        self.hdr_to_key['Feature BFD IPv6'] = 'feature_bfd_ipv6'
        self.hdr_to_key['Feature BFD MAC'] = 'feature_bfd_mac'
        self.hdr_to_key['Feature BFD ALL'] = 'feature_bfd_all'
        self.hdr_to_key['Feature BFD OTHER'] = 'feature_bfd_other'

        self.hdr_to_key['Feature DHCP SNOOP'] = 'feature_dhcp_snoop'
        self.hdr_to_key['Feature DHCP SNOOP IPv4'] = 'feature_dhcp_snoop_ipv4'
        self.hdr_to_key['Feature DHCP SNOOP IPv6'] = 'feature_dhcp_snoop_ipv6'
        self.hdr_to_key['Feature DHCP SNOOP MAC'] = 'feature_dhcp_snoop_mac'
        self.hdr_to_key['Feature DHCP SNOOP ALL'] = 'feature_dhcp_snoop_all'
        self.hdr_to_key['Feature DHCP SNOOP OTHER'] = 'feature_dhcp_snoop_other'

        self.hdr_to_key['Feature DHCP SNOOP FHS'] = 'feature_dhcp_snoop_fhs'
        self.hdr_to_key['Feature DHCP SNOOP FHS IPv4'] = 'feature_dhcp_snoop_fhs_ipv4'
        self.hdr_to_key['Feature DHCP SNOOP FHS IPv6'] = 'feature_dhcp_snoop_fhs_ipv6'
        self.hdr_to_key['Feature DHCP SNOOP FHS MAC'] = 'feature_dhcp_snoop_fhs_mac'
        self.hdr_to_key['Feature DHCP SNOOP FHS ALL'] = 'feature_dhcp_snoop_fhs_all'
        self.hdr_to_key['Feature DHCP SNOOP FHS OTHER'] = 'feature_dhcp_snoop_fhs_other'

        self.hdr_to_key['Feature DHCPv6 RELAY'] = 'feature_dhcpv6_relay'
        self.hdr_to_key['Feature DHCPv6 RELAY IPv4'] = 'feature_dhcpv6_relay_ipv4'
        self.hdr_to_key['Feature DHCPv6 RELAY IPv6'] = 'feature_dhcpv6_relay_ipv6'
        self.hdr_to_key['Feature DHCPv6 RELAY MAC'] = 'feature_dhcpv6_relay_mac'
        self.hdr_to_key['Feature DHCPv6 RELAY ALL'] = 'feature_dhcpv6_relay_all'
        self.hdr_to_key['Feature DHCPv6 RELAY OTHER'] = 'feature_dhcpv6_relay_other'

        self.hdr_to_key['Feature DOT1X'] = 'feature_dot1x'
        self.hdr_to_key['Feature DOT1X IPv4'] = 'feature_dot1x_ipv4'
        self.hdr_to_key['Feature DOT1X IPv6'] = 'feature_dot1x_ipv6'
        self.hdr_to_key['Feature DOT1X MAC'] = 'feature_dot1x_mac'
        self.hdr_to_key['Feature DOT1X ALL'] = 'feature_dot1x_all'
        self.hdr_to_key['Feature DOT1X OTHER'] = 'feature_dot1x_other'

        self.hdr_to_key['Feature DOT1X Multi Auth'] = 'feature_dot1x_multi_auth'
        self.hdr_to_key['Feature DOT1X Multi Auth IPv4'] = 'feature_dot1x_multi_auth_ipv4'
        self.hdr_to_key['Feature DOT1X Multi Auth IPv6'] = 'feature_dot1x_multi_auth_ipv6'
        self.hdr_to_key['Feature DOT1X Multi Auth MAC'] = 'feature_dot1x_multi_auth_mac'
        self.hdr_to_key['Feature DOT1X Multi Auth ALL'] = 'feature_dot1x_multi_auth_all'
        self.hdr_to_key['Feature DOT1X Multi Auth OTHER'] = 'feature_dot1x_multi_auth_other'

        self.hdr_to_key['Feature VxLAN OAM'] = 'feature_vxlan_oam'
        self.hdr_to_key['Feature VxLAN OAM IPv4'] = 'feature_vxlan_oam_ipv4'
        self.hdr_to_key['Feature VxLAN OAM IPv6'] = 'feature_vxlan_oam_ipv6'
        self.hdr_to_key['Feature VxLAN OAM MAC'] = 'feature_vxlan_oam_mac'
        self.hdr_to_key['Feature VxLAN OAM ALL'] = 'feature_vxlan_oam_all'
        self.hdr_to_key['Feature VxLAN OAM OTHER'] = 'feature_vxlan_oam_other'

        self.hdr_to_key['SPAN'] = 'span'
        self.hdr_to_key['SPAN IPv4'] = 'span_ipv4'
        self.hdr_to_key['SPAN IPv6'] = 'span_ipv6'
        self.hdr_to_key['SPAN MAC'] = 'span_mac'
        self.hdr_to_key['SPAN ALL'] = 'span_all'
        self.hdr_to_key['SPAN OTHER'] = 'span_other'

        self.hdr_to_key['Ingress SUP'] = 'ingress_sup'
        self.hdr_to_key['Ingress SUP IPv4'] = 'ingress_sup_ipv4'
        self.hdr_to_key['Ingress SUP IPv6'] = 'ingress_sup_ipv6'
        self.hdr_to_key['Ingress SUP MAC'] = 'ingress_sup_mac'
        self.hdr_to_key['Ingress SUP ALL'] = 'ingress_sup_all'
        self.hdr_to_key['Ingress SUP OTHER'] = 'ingress_sup_other'

        self.hdr_to_key['Netflow/Analytics Filter TCAM'] = 'netflow_analytics_filter_tcam'
        self.hdr_to_key['Netflow/Analytics Filter TCAM MAC'] = 'netflow_analytics_filter_tcam_mac'
        self.hdr_to_key['Netflow/Analytics Filter TCAM IPv4'] = 'netflow_analytics_filter_tcam_ipv4'
        self.hdr_to_key['Netflow/Analytics Filter TCAM IPv6'] = 'netflow_analytics_filter_tcam_ipv6'
        self.hdr_to_key['Netflow/Analytics Filter TCAM ALL'] = 'netflow_analytics_filter_tcam_all'
        self.hdr_to_key['Netflow/Analytics Filter TCAM OTHER'] = 'netflow_analytics_filter_tcam_other'

        self.hdr_to_key['Ingress Dest info table'] = 'ingress_dest_info_table'
        self.hdr_to_key['Ingress IPv4 PACL'] = 'ingress_pacl_ipv4'
        self.hdr_to_key['Ingress IPv6 PACL'] = 'ingress_pacl_ipv6'
        self.hdr_to_key['Ingress IPv4 RACL'] = 'ingress_racl_ipv4'
        self.hdr_to_key['Ingress IPv6 RACL'] = 'ingress_racl_ipv6'
        self.hdr_to_key['Ingress MAC PACL'] = 'ingress_pacl_mac'
        self.hdr_to_key['Ingress Multihop BFD V4'] = 'ingress_multihop_bfd_ipv4'
        self.hdr_to_key['Ingress IPv4+Mac L3 QoS'] = 'ingress_mac_l3_qos_ipv4'
        self.hdr_to_key['Ingress IPv6 L3 QoS'] = 'ingress_l3_qos_ipv6'
        self.hdr_to_key['Ingress IPv4+Mac Port QoS'] = 'ingress_mac_port_qos_ipv4'
        self.hdr_to_key['Ingress IPv6 Port QoS'] = 'ingress_port_qos_ipv6'
        self.hdr_to_key['L4 op labels, Tcam 0'] = 'l4_op_labels_tcam0'
        self.hdr_to_key['L4 op labels, Tcam 1'] = 'l4_op_labels_tcam1'
        self.hdr_to_key['L4 op labels, Tcam 2'] = 'l4_op_labels_tcam2'
        self.hdr_to_key['L4 op labels, Tcam 3'] = 'l4_op_labels_tcam3'
        self.hdr_to_key['L4 op labels, Tcam 4'] = 'l4_op_labels_tcam4'
        self.hdr_to_key['L4 op labels, Tcam 5'] = 'l4_op_labels_tcam5'
        self.hdr_to_key['L4 op labels, Tcam 6'] = 'l4_op_labels_tcam6'
        self.hdr_to_key['L4 op labels, Tcam 7'] = 'l4_op_labels_tcam7'
        self.hdr_to_key['L4 op labels, Tcam 8'] = 'l4_op_labels_tcam8'
        self.hdr_to_key['L4 op labels, Tcam 9'] = 'l4_op_labels_tcam9'
        self.hdr_to_key['L4 op labels, Tcam 10'] = 'l4_op_labels_tcam10'
        self.hdr_to_key['L4 op labels, Tcam 11'] = 'l4_op_labels_tcam11'
        self.hdr_to_key['L4 op labels, Tcam 12'] = 'l4_op_labels_tcam12'
        self.hdr_to_key['L4 op labels, Tcam 13'] = 'l4_op_labels_tcam13'
        self.hdr_to_key['L4 op labels, Tcam 14'] = 'l4_op_labels_tcam14'
        self.hdr_to_key['L4 op labels, Tcam 15'] = 'l4_op_labels_tcam15'
        self.hdr_to_key['L4 op labels, Tcam 16'] = 'l4_op_labels_tcam16'
        self.hdr_to_key['L4 op labels, Tcam 17'] = 'l4_op_labels_tcam17'
        self.hdr_to_key['L4 op labels, Tcam 18'] = 'l4_op_labels_tcam18'
        self.hdr_to_key['Mac Etype/Proto CAM'] = 'mac_etype_proto_cam'
        self.hdr_to_key['LOU'] = 'lou'
        self.hdr_to_key['LOU ip TTL:'] = 'lou_ip_ttl'
        self.hdr_to_key['LOU L4 src port:'] = 'lou_l4_src_port'
        self.hdr_to_key['LOU L4 dst port:'] = 'lou_l4_dst_port'
        self.hdr_to_key['Single LOU Operands'] = 'single_lou_operands'
        self.hdr_to_key['Both LOU Operands'] = 'both_lou_operands'
        self.hdr_to_key['LOU L3 packet len:'] = 'lou_l3_packet_len'
        self.hdr_to_key['LOU IP tos:'] = 'lou_ip_tos'
        self.hdr_to_key['LOU IP dscp:'] = 'lou_ip_dscp'
        self.hdr_to_key['LOU ip precedence:'] = 'lou_ip_precedence'


        self.hdr_to_key['Egress CNTACL'] = 'egress_cntacl'
        self.hdr_to_key['Egress CNTACL ALL'] = 'egress_cntacl_all'
        self.hdr_to_key['Egress CNTACL MAC'] = 'egress_cntacl_mac'
        self.hdr_to_key['Egress CNTACL IPv4'] = 'egress_cntacl_ipv4'
        self.hdr_to_key['Egress CNTACL IPv6'] = 'egress_cntacl_ipv6'
        self.hdr_to_key['Egress CNTACL OTHER'] = 'egress_cntacl_other'
        self.hdr_to_key['Egress CNTACL OTHER'] = 'egress_cntacl_other'

        self.hdr_to_key['Ingress CNTACL'] = 'ingress_cntacl'
        self.hdr_to_key['Ingress CNTACL ALL'] = 'ingress_cntacl_all'
        self.hdr_to_key['Ingress CNTACL MAC'] = 'ingress_cntacl_mac'
        self.hdr_to_key['Ingress CNTACL IPv4'] = 'ingress_cntacl_ipv4'
        self.hdr_to_key['Ingress CNTACL IPv6'] = 'ingress_cntacl_ipv6'
        self.hdr_to_key['Ingress CNTACL OTHER'] = 'ingress_cntacl_other'
        self.hdr_to_key['Ingress CNTACL OTHER'] = 'ingress_cntacl_other'

        self.hdr_to_key['Redirect IPv4'] = 'redirect_ipv4'
        self.hdr_to_key['Redirect IPv6'] = 'redirect_ipv6'
        self.hdr_to_key['Protocol CAM'] = 'protocol_cam'
        self.hdr_to_key['TCP Flags'] = 'tcp_flags'
        self.hdr_to_key['UDF Span IPv4'] = 'udf_span_ipv4'

        # EOR
        self.hdr_to_key['Egress IPv4 RACL'] = 'egress_racl_ipv4'
        self.hdr_to_key['Egress IPv6 RACL'] = 'egress_racl_ipv6'

        # N3K-C3264C-E
        self.hdr_to_key['Ingress IPv4 RACL Lite'] = 'ingress_ipv4_racl_lite'
        self.hdr_to_key['Ingress IPv4 L3 QoS (Intra-TCAM Lite)'] = 'ingress_ipv4_l3_qos_intra_tcam_lite'
        self.hdr_to_key['SUP COPP'] = 'sup_copp'
        self.hdr_to_key['SUP COPP Reason Code TCAM'] = 'sup_copp_reason_code_tcam'
        self.hdr_to_key['Redirect'] = 'redirect'
        self.hdr_to_key['VPC Convergence'] = 'vpc_convergence'
        self.hdr_to_key['COPP_SYSTEM'] = 'copp_system'
        # trailing space is required in the following keys as of 10.1(2)
        self.hdr_to_key['IPv6 Src Compression '] = 'ipv6_src_compression'
        self.hdr_to_key['IPv6 Dest Compression '] = 'ipv6_dest_compression'

        # N9K-SUP-B + N9K-X9732C-EX
        self.hdr_to_key['Feature DHCP VACL FHS'] = 'feature_dhcp_vacl_fhs'
        self.hdr_to_key['Feature DHCP VACL FHS IPv4'] = 'feature_dhcp_vacl_fhs_ipv4'
        self.hdr_to_key['Feature DHCP VACL FHS IPv6'] = 'feature_dhcp_vacl_fhs_ipv6'
        self.hdr_to_key['Feature DHCP VACL FHS MAC'] = 'feature_dhcp_vacl_fhs_mac'
        self.hdr_to_key['Feature DHCP VACL FHS ALL'] = 'feature_dhcp_vacl_fhs_all'
        self.hdr_to_key['Feature DHCP VACL FHS OTHER'] = 'feature_dhcp_vacl_fhs_other'
        self.hdr_to_key['Feature DHCP SISF'] = 'feature_dhcp_sisf'
        self.hdr_to_key['Feature DHCP SISF IPv4'] = 'feature_dhcp_sisf_ipv4'
        self.hdr_to_key['Feature DHCP SISF IPv6'] = 'feature_dhcp_sisf_ipv6'
        self.hdr_to_key['Feature DHCP SISF MAC'] = 'feature_dhcp_sisf_mac'
        self.hdr_to_key['Feature DHCP SISF ALL'] = 'feature_dhcp_sisf_all'
        self.hdr_to_key['Feature DHCP SISF OTHER'] = 'feature_dhcp_sisf_other'

    def _get_instance_dict_from_module_dict(self):
        '''
        Populates self._instance_dict, given self._module_dict

        self._instance_dict is empty, if expected keys are not present.  
        Else, self._instance_dict contains the following keys:
            inst - instance ID
            TABLE_resource_util_info - dictionary containing the following:
                ROW_resource_util_info - a list of dictionaries with the following keys:
                    resource_hdr - description of resource
                    ents_use - used tcam entries
                    ents_free - free tcam entries
                    ents_pctage - percentage of tcam used

        "TABLE_instance": {
            "ROW_instance": [
                {               <<<<<<<<< self._instance_dict
                    "inst": "0x0", 
                    "TABLE_resource_util_info": {
                        "ROW_resource_util_info": [
                            {
                                "resource_hdr": "Ingress IPv4 PACL", 
                                "ents_use": "0", 
                                "ents_free": "1024", 
                                "ents_pctage": "0.00"
                            },


        '''
        if self.module == None:
            self.log.warning('returning empty dict(). self.module is not set')
            return dict()
        try:
            _instance_list = self._convert_to_list(self._module_dict['TABLE_instance']['ROW_instance'])
        except:
            self.log.warning('returning empty dict() [TABLE_instance][ROW_instance] not found in self._module_dict'.format(self._module_dict))
            return dict()
        self._instance_dict = dict()
        for d in _instance_list:
            if 'inst' not in d:
                self.log.warning('Skipping. key [inst] not found in d {}'.format(d))
                continue
            inst = d['inst']
            self._instance_dict[inst] = d


    def _get_resource_util_info_dict_from_instance_dict(self):
        '''
        Given self._instance_dict, populate self._resource_util_info_dict

        self._resource_util_info_dict is empty, if expected keys are not present in self._instance_dict.  
        Else, self._resource_util_info_dict has the following structure:
            self._resource_util_info_dict[inst]['copp_ipv4_mac'] = dict()
            self._resource_util_info_dict[inst]['copp_ipv6_mac'] = dict()
            etc, for all keys in self.hdr_to_key

            each dict() contains the following key/values (values have been converted from str() to int() / float())
            self._resource_util_info_dict[inst]['copp_ipv4_mac']['used']    = ents_use
            self._resource_util_info_dict[inst]['copp_ipv4_mac']['free']    = ents_free
            self._resource_util_info_dict[inst]['copp_ipv4_mac']['percent'] = ents_pctage
            self._resource_util_info_dict[inst]['copp_ipv4_mac']['title']   = resource_hdr

        "TABLE_instance": {
            "ROW_instance": [
                {               <<<<<<<<< self._instance_dict
                    "inst": "0x0", 
                    "TABLE_resource_util_info": {
                        "ROW_resource_util_info": [
                            {  <<<<<<<<<<<<<<<<<<<<<<<<<<<< _resource_info_util_dict
                                "resource_hdr": "Ingress IPv4 PACL", 
                                "ents_use": "0", 
                                "ents_free": "1024", 
                                "ents_pctage": "0.00"
                            },


        '''
        def fix_fields(d):
            '''
            return a dictionary with a consistent set of fields by adding any fields that are in _mandatory_fields to 
            the returned dictionary and assigning a value of None.
            '''
            missing_fields = list()
            _mandatory_fields = list()
            _mandatory_fields.append('resource_hdr')
            _mandatory_fields.append('ents_use')
            _mandatory_fields.append('ents_free')
            _mandatory_fields.append('ents_pctage')
            for _field in _mandatory_fields:
                if _field not in d:
                    d[_field] = -1
            return d

        self._resource_util_info_dict = dict()
        for inst in self._instance_dict:
            try:
                resource_info_util_list = self._convert_to_list(self._instance_dict[inst]['TABLE_resource_util_info']['ROW_resource_util_info'])
            except:
                self.log.warning('self._resource_util_info_dict is empty due to [TABLE_resource_util_info][ROW_resource_util_info] not found in self._instance_dict {}')
                return
            self._resource_util_info_dict[inst] = dict()
            for d in resource_info_util_list:
                d_fixed = fix_fields(d)
                if d_fixed['resource_hdr'] not in self.hdr_to_key:
                    self.log.warning('Skipping ({}). Not in self.hdr_to_key'.format(d_fixed['resource_hdr']))
                    continue
                key = self.hdr_to_key[d_fixed['resource_hdr']]
                self._resource_util_info_dict[inst][key] = dict()
                self._resource_util_info_dict[inst][key]['used'] = int(d_fixed['ents_use'])
                self._resource_util_info_dict[inst][key]['free'] = int(d_fixed['ents_free'])
                self._resource_util_info_dict[inst][key]['percent'] = float(d_fixed['ents_pctage'])
                self._resource_util_info_dict[inst][key]['title'] = d_fixed['resource_hdr']


class NxapiAccessListResourceUtilization(NxapiAccessList):
    '''
    Methods/properties to retrieve ACL TCAM info using:

    show system internal access-list resource utilization module X

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self._resource_util_info_dict = dict()
        self._instance_dict = dict()
        self._module_dict = dict()
        self._refreshed = False

    def refresh(self):
        if self.module == None:
            self.log.error('Exiting. Please call <instance>.module = X first')
            exit(1)
        self.cli = 'show system internal access-list resource utilization module {}'.format(self.module)
        self.show(self.cli)
        self._get_module_dict()
        self._get_instance_dict_from_module_dict()
        self._get_resource_util_info_dict_from_instance_dict()
        self._refreshed = True


    def get_all_free(self,key):
        '''
        if key is present, returns a dictionary, keyed on asic instance, whose value is free entries for key
        if key is not present, returns an empty dictionary
        '''
        _dict = dict()
        for inst in self._resource_util_info_dict:
            try:
                _dict[inst] = self._resource_util_info_dict[inst][key]['free']
            except:
                #self.log.error('hit exception with key {}. Returning empty dict'.format(key))
                return dict()
        return _dict

    def get_all_percent(self,key):
        '''
        if key is present, returns a dictionary, keyed on asic instance, whose value is percentage used by key
        if key is not present, returns an empty dictionary
        '''
        _dict = dict()
        for inst in self._resource_util_info_dict:
            try:
                _dict[inst] = self._resource_util_info_dict[inst][key]['percent']
            except:
                #self.log.error('hit exception with key {}. Returning empty dict'.format(key))
                return dict()
        return _dict

    def get_all_used(self,key):
        '''
        if key is present, returns a dictionary, keyed on asic instance, whose value is entries used by key
        if key is not present, returns an empty dictionary
        '''
        _dict = dict()
        for inst in self._resource_util_info_dict:
            try:
                _dict[inst] = self._resource_util_info_dict[inst][key]['used']
            except:
                #self.log.error('hit exception with key {}. Returning empty dict'.format(key))
                return dict()
        return _dict

    def get_max_percent(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['percent'])
            except:
                return -1
        return max(_values_list)

    def get_min_percent(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['percent'])
            except:
                return -1
        return min(_values_list)

    def get_max_free(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['free'])
            except:
                return -1
        return max(_values_list)

    def get_min_free(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['free'])
            except:
                return -1
        return min(_values_list)

    def get_max_used(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['used'])
            except:
                return -1
        return max(_values_list)

    def get_min_used(self,key):
        _values_list = list()
        for inst in self._resource_util_info_dict:
            try:
                _values_list.append(self._resource_util_info_dict[inst][key]['used'])
            except:
                return -1
        return min(_values_list)

    def verify_prequisites(self):
        if self.feature == None:
            self.log.error('Exiting. Please set feature first e.g. acl.feature = "span_ipv4"')
            exit(1)
        if self._refreshed == False:
            self.log.error('Exiting. Please call refresh() first. e.g. acl.refresh()')
            exit(1)

    @property
    def max_free(self):
        self.verify_prequisites()
        return self.get_max_free(self.feature)

    @property
    def min_free(self):
        self.verify_prequisites()
        return self.get_min_free(self.feature)

    @property
    def max_percent(self):
        self.verify_prequisites()
        return self.get_max_percent(self.feature)

    @property
    def min_percent(self):
        self.verify_prequisites()
        return self.get_min_percent(self.feature)

    @property
    def max_used(self):
        self.verify_prequisites()
        return self.get_max_used(self.feature)

    @property
    def min_used(self):
        self.verify_prequisites()
        return self.get_min_used(self.feature)

    @property
    def all_free(self):
        '''
        returns a dictionary, keyed on tcam instance, values are the entries free for each tcam instance
        '''
        self.verify_prequisites()
        return self.get_all_free(self.feature)

    @property
    def all_percent(self):
        '''
        returns a dictionary, keyed on tcam instance, values are the percent used entries for each tcam instance
        '''
        self.verify_prequisites()
        return self.get_all_percent(self.feature)

    @property
    def all_used(self):
        '''
        returns a dictionary, keyed on tcam instance, values are the entries used for each tcam instance
        '''
        self.verify_prequisites()
        return self.get_all_used(self.feature)

    @property
    def module(self):
        return self._module
    @module.setter
    def module(self,_x):
        if not self.verify.is_digits(_x):
            self.log.error('Exiting. module must be an integer.  Got {}'.format(_x))
            exit(1)
        self._module = _x

    @property
    def feature(self):
        return self._feature
    @feature.setter
    def feature(self,_x):
        if _x not in self.hdr_to_key.values():
            self.log.error('Exiting. Unknown feature {}'.format(_x))
            exit(1)
        self._feature = _x

    @property
    def features(self):
        return sorted(self.hdr_to_key.values())
