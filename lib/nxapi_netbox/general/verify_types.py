"""
verify_types.py
Summary: Methods for verifying types (e.g. int, str) and formats (mac address, ipv4 address)
"""
import ipaddress
import logging
import math  # is_power()
import re
import string

# local libraries
from nxapi_netbox.general.constants import Constants

OUR_VERSION = 135

class VerifyTypes:
    """
    methods to verify various types e.g. boolean, int, str, hex values, etc

    Example usage:

    from verify_types import VerifyTypes()
    verify = VerifyTypes()
    myMac = ":_LLLL"
    if not verify.is_mac_address(myMac):
        print("{} not a mac-address.".format(myMac))

    """

    def __init__(self, log):
        super().__init__()
        self.lib_version = OUR_VERSION
        self.lib_name = "VerifyTypes"
        self.log = log
        self.constants = Constants()

    def is_boolean(self, param):
        """verify x is a boolean value"""
        if isinstance(param, bool):
            return True
        return False

    def is_digits(self, param):
        """verify x contains only digits i.e. is a positive integer"""
        if not self.constants.RE_DIGITS.search(str(x)):
            return False
        return True

    def is_float(self, param):
        """verify x is a float"""
        if isinstance(param, float):
            return True
        return False

    def is_hex(self, param):
        """
        verify x contains only hexidecimal characters
        """
        if not self.constants.HEX_DIGITS.issuperset(x):
            return False
        return True

    def is_int(self, param):
        """verify x is an integer"""
        if isinstance(param, int):
            return True
        return False

    def is_ipv4_address(self, param):
        """verify x is an ipv4 address"""
        try:
            if isinstance(ipaddress.IPv4Address(param), ipaddress.IPv4Address):
                return True
            return False
        except Exception as general_exception:
            self.log.error(f"Got exception: {general_exception}"
            return False

    def is_ipv4_address_with_prefix(self, param):
        """
        verify x is an ipv4 address with prefix of the form X.X.X.X/Y
        """
        try:
            if isinstance(ipaddress.IPv4Interface(param), ipaddress.IPv4Interface):
                return True
            return False
        except Exception as general_exception:
            self.log.error(f"Got exception: {general_exception}")
            return False

    def is_ipv4_network(self, param):
        try:
            if isinstance(ipaddress.IPv4Address(param), ipaddress.IPv4Network):
                return True
            return False
        except Exception as general_exception:
            self.log.error(f"Got exception: {general_exception}")
            return False

    def is_ipv4_mask(self, param):
        if not isinstance(param, int):
            self.log.debug(
                f"bad ipv4 network mask.Expected an integer. Got {param}"
            )
            return False
        if x not in self.constants.IPV4_MASK_RANGE:
            msg = f"bad ipv4 network mask {param}"
            msg += f"Should be an int {self.constants.IPV4_MASK_RANGE.start} >= x"
            msg += f" <= {self.constants.IPV4_MASK_RANGE.stop - 1}."
            self.log.debug(msg)
            return False
        return True

    def is_ipv4_unicast_address(self, param):
        """verify x is an ipv4 address"""
        if not self.is_ipv4_address(x):
            return False
        _ = ipaddress.IPv4Address(x)
        bad_type = ""
        if _.is_multicast:
            bad_type = "is_multicast"
        elif _.is_loopback:
            bad_type = "is_loopback"
        elif _.is_reserved:
            bad_type = "is_reserved"
        elif _.is_unspecified:
            bad_type = "is_unspecified"
        elif _.is_link_local:
            bad_type = "is_link_local"
        elif re.search("\/", x):
            bad_type = "is_subnet"
        if bad_type != "":
            self.log.debug(f"{param} not a unicast ipv4 address -> {bad_type}")
            return False
        return True

    def is_ipv6_network(self, param):
        """verify param is a valid ipv6 network mask"""
        try:
            if isinstance(ipaddress.IPv4Address(param), ipaddress.IPv6Network):
                return True
            return False
        except Exception as general_exception:
            self.log.error(f"Got exception: {general_exception}")
            return False

    def is_ipv6_mask(self, param):
      """verify param is a valid ipv6 network mask"""
        if not isinstance(param, int):
            self.log.debug(f"bad ipv6 network mask {param}. Should be an integer.")
            return False
        if x not in self.constants.IPV6_MASK_RANGE:
            msg = f"bad ipv6 network mask {param}"
            msg += f"Should be an int {self.constants.IPV6_MASK_RANGE.start} >= x"
            msg += f" <= {self.constants.IPV6_MASK_RANGE.stop - 1}."
            self.log.debug(msg)
            return False
        return True

    def is_ipv6_address(self, param):
        """
        verify param is an ipv6 address
        """
        try:
            if isinstance(ipaddress.IPv6Address(param), ipaddress.IPv6Address):
                return True
            return False
        except Exception as general_exception:
            self.log.error(f"Got exception: {general_exception}")
            return False

    def is_ipv6_link_local_address(self, param):
        """
        verify param is an ipv6 link-local address
        """
        if not self.is_ipv6_address(param):
            return False
        if not ipaddress.IPv6Address(param).is_link_local:
            return False
        return True

    def is_ipv6_unicast_address(self, param):
        """
        verify param is an ipv6 unicast address
        """
        if not self.is_ipv6_address(param):
            return False
        _ = ipaddress.IPv6Address(param)
        bad_type = ""
        if _.is_multicast:
            bad_type = "is_multicast"
        elif _.is_loopback:
            bad_type = "is_loopback"
        elif _.is_reserved:
            bad_type = "is_reserved"
        elif _.is_unspecified:
            bad_type = "is_unspecified"
        elif _.is_link_local:
            bad_type = "is_link_local"
        elif re.search("\.0$", param):
            bad_type = "is_subnet"
        if bad_type != "":
            self.log.error(f"{param} not a unicast ipv6 address -> {bad_type}")
            return False
        return True

    def is_logging_instance(self, param):
        """
        return True if param is a logging instance
        else, return False
        """
        if isinstance(param, logging.Logger):
            return True
        return False

    def is_loglevel(self, param):
        """
        return True if x is a valid logging level
        else, return False
        """
        if param in self.constants.VALID_LOGLEVELS:
            return True
        return False

    def is_dict(self, param):
        """verify x is a dictionary"""
        if isinstance(param, dict):
            return True
        return False

    def is_list(self, param):
        """verify x is a list"""
        if isinstance(param, list):
            return True
        return False

    def is_list_of_int(self, param):
        """verify x is a list containing only integers"""
        if not isinstance(param, list):
            return False
        for item in param:
            if not isinstance(item, int):
                return False
        return True

    def is_mac_address(self, param):
        """
        Return True if param is a mac address
        Else, return False

        This returns True for only three formats for mac address,
        as shown below:

        ab-cd-eF-12-34-56
        ab:cd:eF:12:34:56
        abcd.eF12.3456

        For everything else, it returns False
        """
        if self.constants.RE_MAC_COLON.search(param):
            return True
        if self.constants.RE_MAC_HYPHEN.search(param):
            return True
        if self.constants.RE_MAC_PERIOD.search(param):
            return True
        return False

    def is_power(self, x, b):
        """
        verify x is a power of b
        Examples:
            is_power(8,2)  # True
            is_power(7,2)  # False
        """
        if b == 1:
            return x == 1
        return b ** int(math.log(x, b) + 0.5) == x

    def is_range(self, param):
        if isinstance(param, range):
            return True
        return False

    def is_tuple(self, param):
        if isinstance(param, tuple):
            return True
        return False
