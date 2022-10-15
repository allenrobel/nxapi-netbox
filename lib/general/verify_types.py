'''
verify_types.py
Summary: Methods for verifying types (e.g. int, str) and formats (mac address, ipv4 address)
Author: Allen Robel
Email: arobel@cisco.com
'''
our_version = 135

# standard libraris
import ipaddress
import logging
import math                # is_power()
import re
# local libraries
from general.constants import Constants
class VerifyTypes(Constants):
    '''
    methods to verify various types e.g. boolean, int, str, hex values, etc

    Example usage:

    from verify_types import VerifyTypes()
    verify = VerifyTypes()
    myMac = ":_LLLL"
    if not verify.is_mac_address(myMac):
        print("{} not a mac-address.".format(myMac))

    '''
    def __init__(self, log):
        super().__init__()
        self.lib_version = our_version
        self.lib_name = "VerifyTypes"
        self.log = log
        self.DEFAULT_LOGLEVEL = 'INFO'
        self.ipv4_mask_range = range(0, self.ipv4_mask_length + 1)
        self.ipv6_mask_range = range(0, self.ipv6_mask_length + 1)
        self.re_digits = re.compile('^(\d+)$')
        self.re_mac_address = re.compile(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2}$)', re.I)

    def is_boolean(self,x):
        '''verify x is a boolean value'''
        if isinstance(x, bool):
            return True
        return False

    def is_digits(self,x):
        '''verify x contains only digits i.e. is a positive integer'''
        if not self.re_digits.search(str(x)):
            return False
        return True

    def is_float(self,x):
        '''verify x is a float'''
        if isinstance(x, float):
            return True
        return False

    def is_hex(self,x):
        '''
        verify x contains only hexidecimal characters
        '''
        if not self.HEX_DIGITS.issuperset(x):
            return False
        return True

    def is_int(self,x):
        '''verify x is a integer'''
        if isinstance(x, int):
            return True
        return False

    def is_ipv4_address(self,x):
        '''verify x is an ipv4 address'''
        try:
            _ = ipaddress.IPv4Address(x)
            if isinstance(_, ipaddress.IPv4Address):
                return True
            else:
                return False
        except Exception as e:
            self.log.error('Got exception: {}'.format(e))
            return False

    def is_ipv4_address_with_prefix(self,x):
        '''
        verify x is an ipv4 address with prefix of the form X.X.X.X/Y
        '''
        try:
            _ = ipaddress.IPv4Interface(x)
            if isinstance(_, ipaddress.IPv4Interface):
                return True
            else:
                return False
        except Exception as e:
            self.log.error('Got exception: {}'.format(e))
            return False

    def is_ipv4_network(self,x):
        try:
            _ = ipaddress.IPv4Address(x)
            if isinstance(_, ipaddress.IPv4Network):
                return True
            else:
                return False
        except Exception as e:
            self.log.error('Got exception: {}'.format(e))
            return False

    def is_ipv4_mask(self,x):
        if not isinstance(x, int):
            self.log.debug("bad ipv4 network mask.Expected an integer. Got {}".format(x))
            return False
        if x not in self.ipv4_mask_range:
            self.log.debug("bad ipv4 network mask {}. Should be an int {} >= x <= {} .".format(
                x,
                self.ipv4_mask_range.start,
                self.ipv4.mask_range.stop -1))
            return False
        return True

    def is_ipv4_unicast_address(self,x):
        '''verify x is an ipv4 address'''
        if not self.is_ipv4_address(x):
            return False
        _ = ipaddress.IPv4Address(x)
        bad_type = ''
        if _.is_multicast:
            bad_type = 'is_multicast'
        elif _.is_loopback:
            bad_type = 'is_loopback'
        elif _.is_reserved:
            bad_type = 'is_reserved'
        elif _.is_unspecified:
            bad_type = 'is_unspecified'
        elif _.is_link_local:
            bad_type = 'is_link_local'
        elif re.search('\/', x):
            bad_type = 'is_subnet'
        if bad_type != '':
            self.log.debug("{} not a unicast ipv4 address -> {}".format(x, bad_type))
            return False
        return True

    def is_ipv6_network(self,x):
        try:
            _ = ipaddress.IPv4Address(x)
            if isinstance(_, ipaddress.IPv6Network):
                return True
            else:
                return False
        except Exception as e:
            self.log.error('Got exception: {}'.format(e))
            return False

    def is_ipv6_mask(self,x):
        if not isinstance(x, int):
            self.log.debug("bad ipv6 network mask {}. Should be an integer.".format(x))
            return False
        if x not in self.ipv6_mask_range:
            self.log.debug("bad ipv6 network mask {}. Should be int {} >= x <= {} .".format(
                x,
                self.ipv6_mask_range.start,
                self.ipv6.mask_range.stop -1))
            return False
        return True

    def is_ipv6_address(self, x):
        '''
        verify x is an ipv6 address
        '''
        try:
            _ = ipaddress.IPv6Address(x)
            if isinstance(_, ipaddress.IPv6Address):
                return True
            else:
                return False
        except Exception as e:
            self.log.error('Got exception: {}'.format(e))
            return False

    def is_ipv6_link_local_address(self, x):
        '''
        verify x is an ipv6 link-local address
        '''
        if not self.is_ipv6_address(x):
            return False
        _ = ipaddress.IPv6Address(x)
        if not _.is_link_local:
            return False
        return True
        
    def is_ipv6_unicast_address(self, x):
        '''
        verify x is an ipv6 unicast address
        '''
        if not self.is_ipv6_address(x):
            return False
        _ = ipaddress.IPv6Address(x)
        bad_type = ''
        if _.is_multicast:
            bad_type = 'is_multicast'
        elif _.is_loopback:
            bad_type = 'is_loopback'
        elif _.is_reserved:
            bad_type = 'is_reserved'
        elif _.is_unspecified:
            bad_type = 'is_unspecified'
        elif _.is_link_local:
            bad_type = 'is_link_local'
        elif re.search('\.0$', x):
            bad_type = 'is_subnet'
        if bad_type != '':
            self.log.error("{} not a unicast ipv6 address -> {}".format(x, bad_type))
            return False
        return True

    def is_logging_instance(self, x):
        '''
        return True if x is a logging instance
        else, return False
        '''
        if isinstance(x, logging.Logger):
            return True
        return False

    def is_loglevel(self, x):
        if x in self.VALID_LOGLEVELS:
            return True
        return False

    def is_dict(self, x):
        '''verify x is a dictionary'''
        if isinstance(x, dict):
            return True
        return False

    def is_list(self, x):
        '''verify x is a list'''
        if isinstance(x, list):
            return True
        return False

    def is_list_of_int(self, x):
        '''verify x is a list containing only integers'''
        if not isinstance(x, list):
            return False
        for e in x:
            if not isinstance(e, int):
                self.log.error("One or more elements of list are not integers: {}".format(x))
                return False
        return True

    def is_mac_address(self, x):
        '''verify x is a mac address'''
        m = self.re_mac_address.search(x)
        if m:
            return True
        return False

    def is_power(self, x, b):
        '''
        verify x is a power of b
        Examples:
            is_power(8,2)  # True
            is_power(7,2)  # False
        '''
        if b == 1:
            return x == 1
        return b**int(math.log(x, b)+.5) == x

    def is_range(self, x):
        if isinstance(x, range):
            return True
        self.log.error("Constants.is_range: Not a python range() type. Expected range(x,y). Got {}".format(x))
        return False

    def is_tuple(self, x):
        if isinstance(x, tuple):
            return True
        return False
