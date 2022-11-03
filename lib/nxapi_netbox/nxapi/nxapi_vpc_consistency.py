'''
Name: nxapi_vpc_consistency.py
Author: Allen Robel (arobel@cisco.com)
Description: methods which collect/return information about vpc consistency parameters

Example usage:
'''
import re
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

our_version = 107

class NxapiVpcConsistency(NxapiBase):
    '''
        This class creates info_dict which contains a list of dictionaries,
        where each dictionary contains the keys shown in the object below i.e.:
        vpc-param-name
        vpc-param-type
        vpc-param-local-val
        vpc-param-peer-val

        If info_dict is empty due to this library encountering an error self.error_reason will be set,
        and self.error dict will be populated with self.error['error'] = self.error_reason

        Also created are the following properties

        inconsistent_params()

        Which returns either:
        1. a list of dictionaries containing inconsistent paramters (if any), see make_info_dict() for the structure
        2. an empty list if all parameters are consistent
        3. a list of one dictionary containing the key 'error' whose value is the error encountered

        {
            "TABLE_vpc_consistency": {
                "ROW_vpc_consistency": [
                    {
                        "vpc-param-name": "STP MST Simulate PVST", 
                        "vpc-param-type": "1", 
                        "vpc-param-local-val": "Enabled", 
                        "vpc-param-peer-val": "Enabled"
                    }, 
                    etc,
                ]
            }
        }

       all_params()

       Which returns either:

        1. a list of dictionaries containing all paramters, see make_info_dict() for the structure
        2. a list of one dictionary containing the key 'error' whose value is the error encountered

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict()
        self.error = dict()
        self._error_reason = None
        self.lib_version = our_version
        self.class_name = 'NxapiVpcConsistency'
        self.timeout = 20
        self._inconsistent_params = list()
        self._all_params = list()
        self._mismatched_labels = list()
        self.cli = None
        # keyed on label
        # value is a dict() keyed on label whose value is length of names and labels
        # [label][names] = len(vpc-param-name)
        # [label][params] = len(vpc-param-local-val)
        self._mismatched_info = dict()

    def refresh(self):
        if self.cli == None:
            self.log.error('exiting. self.cli is not set.')
            exit(1)
        self.show()
        self.make_info_dict()
        self.verify_vpc_param_val_present()

    def make_info_dict_error(self):
        self.log.debug(self.error_reason)
        self.error = dict()
        self.error['error'] = self.error_reason
        self.info = [self.error]

    def make_info_dict(self):
        '''
        from self.body[0] populate self.info list(),
        list() elements will be either:

        1. dict() with the following keys:
            vpc-param-name
            vpc-param-type
            vpc-param-local-val
            vpc-param-peer-val

        2. dict() with the following key:

            error

        In case 2, the value will be a description of the error
        '''
        self.info = dict()
        self.error = dict()
        self.error_reason = None

        if self.body_length != 1:
            self.log.error('{} early return: unexpected body_length {}'.format(self.hostname, self.body_length))
            return
        try:
            self.info = self._convert_to_list(self.body[0]['TABLE_vpc_consistency']['ROW_vpc_consistency'])
        except:
            self.log.error('{} early return. [TABLE_vpc_consistency][ROW_vpc_consistency] not present in self.body[0] {}'.format(self.hostname, self.body[0]))
            self.error_reason = '{} is feature vpc enabled?'.format(self.hostname)
            self.make_info_dict_error()
            return

    def print_dict(self):
        '''
        print the contents of self.info
        '''
        row_index = 0
        for row in self.info:
            self.log.debug('{} self.info[{}] = {}'.format(self.hostname, row_index, self.info[row_index]))
            row_index += 1

    @property
    def error_reason(self):
        return self._error_reason
    @error_reason.setter
    def error_reason(self, _x):
        self._error_reason = _x
    
    def verify_vpc_param_val_present(self):
        '''
        verify_vpc_param_val_present works only for consistency parameters for which the
        following keys are expected:

        vpc-param-local-val
        vpc-param-peer-val

        For example 'show vpc consistency-parameters vlans' is not expected to have the above keys,
        so this method will fail if called from class NxapiVpcConsistencyVlans()
        '''
        if len(self.info) == 0:
            self.log.error('exiting. self.info is empty. was instance.refresh() called?')
            exit(1)

        for d in self.info:
            if 'vpc-param-local-val' not in d:
                self.log.error('vpc-param-local-val not found in d {}'.format(d))
                exit(1)
            if 'vpc-param-peer-val' not in d:
                self.log.error('vpc-param-peer-val not found in d {}'.format(d))
                exit(1)

    @property
    def inconsistent_params(self):
        '''
        inconsistent_params() works only for consistency parameters for which the
        following keys are expected:

        vpc-param-local-val
        vpc-param-peer-val

        For example 'show vpc consistency-parameters vlans' is not expected to have
        the above keys, so this method will fail if called from class 
        NxapiVpcConsistencyVlans()

        In subclass NxapiVpcConsistencyVlans() we override this property
        '''
        self._inconsistent_params = list()
        if self.error_reason != None:
            self._inconsistent_params.append(self.error)
            return self._inconsistent_params
        self.verify_vpc_param_val_present()
        for d in self.info:
            if d['vpc-param-local-val'] != d['vpc-param-peer-val']:
                self._inconsistent_params.append(d)
        return self._inconsistent_params

    @property
    def all_params(self):
        self._all_params = list()
        if self.error_reason != None:
            self._all_params.append(self.error)
            return self._all_params
        for d in self.info:
            self._all_params.append(d)
        return self._all_params

    @property
    def mismatched_info(self):
        return self._mismatched_info

    @property
    def mismatched_labels(self):
        self._mismatched_labels = list()
        if self.error_reason != None:
            self._inconsistent_params.append(self.error)
            return self._mismatched_labels
        self._mismatched_info = dict()
        for d in self.info:
            self._mismatched_info = dict()
            self._param_name_length = len(re.split(',', d['vpc-param-name']))
            self._param_local_length = len(re.split(',', d['vpc-param-local-val']))
            if self._param_name_length != self._param_local_length:
                self._mismatched_labels.append(d)
                self.log.info('names {} values {} : {}'.format(self._param_name_length, self._param_local_length, d['vpc-param-name']))
                _label = d['vpc-param-name']
                self._mismatched_info[_label] = dict()
                self._mismatched_info[_label]['names'] = self._param_name_length
                self._mismatched_info[_label]['params'] = self._param_local_length
        return self._mismatched_labels


class NxapiVpcConsistencyGlobal(NxapiVpcConsistency):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.class_name = 'NxapiVpcConsistencyGlobal'
        self.param_type = 'global'
        self.cli = 'show vpc consistency-parameters global'

   # def refresh(self):
   #     self.show()
   #     self.make_info_dict()

class NxapiVpcConsistencyVni(NxapiVpcConsistency):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.class_name = 'NxapiVpcConsistencyVni'
        self.param_type = 'vni'
        self.cli = 'show vpc consistency-parameters vni'


class NxapiVpcConsistencyVlans(NxapiVpcConsistency):
    '''
    The JSON structure for this CLI differs from the others:

    {
        "vpc-param-name": "STP MST Region Revision",
        "vpc-param-type": "1",
        "reason_code": "SUCCESS",
        "vpc-pass-vlans": "0-4095"
    },

    We override self.inconsistent_params to consider only that
    reason_code == SUCCESS.  If reason_code != SUCCESS, we add
    that element to self._inconsistent_params list()

    '''

    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.class_name = 'NxapiVpcConsistencyVlans'
        self.param_type = 'vlans'
        self.cli = 'show vpc consistency-parameters vlans'
    def refresh(self):
        self.cli = 'show vpc consistency-parameters vlans'
        self.show()
        self.make_info_dict()

    @property
    def inconsistent_params(self):
        '''
        '''
        self._inconsistent_params = list()
        if self.error_reason != None:
            self._inconsistent_params.append(self.error)
            return self._inconsistent_params
        for d in self.info:
            if d['reason_code'] != 'SUCCESS':
                self._inconsistent_params.append(d)
        return self._inconsistent_params


class NxapiVpcConsistencyInterface(NxapiVpcConsistency):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.class_name = 'NxapiVpcConsistencyInterface'
        self.param_type = 'interface'
        self._interface = None
    def refresh(self):
        if self.interface == None:
            self.log.error('exiting. please call instance.interface = <interface> before calling instance.refresh()')
        self.cli = 'show vpc consistency-parameters interface {}'.format(self.interface)
        self.show()
        self.make_info_dict()
        self.verify_vpc_param_val_present()

    @property
    def interface(self):
        return self._interface
    @interface.setter
    def interface(self, _x):
        self._interface = _x
