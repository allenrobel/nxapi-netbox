#!/usr/bin/env python3
"""
Description: Constants used by nxapi-netbox libraries
"""
import re

OUR_VERSION = 102
class Constants:
    """
    Constants used by nxapi-netbox libraries
    """
    def __init__(self):
        self.lib_name = "Constants"
        self.lib_version = OUR_VERSION
        self.DEFAULT_LOGLEVEL = "INFO"
        self.IPV4_MASK_LENGTH = 32
        self.IPV6_MASK_LENGTH = 128
        self.IPV4_MASK_RANGE = range(0, self.IPV4_MASK_LENGTH + 1)
        self.IPV6_MASK_RANGE = range(0, self.IPV6_MASK_LENGTH + 1)
        self.DEFAULT_LOGLEVEL = "INFO"
        self.VALID_LOGLEVELS = ["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL"]
        self.HEX_DIGITS = frozenset("0123456789ABCDEFabcdef")
        self.RE_DIGITS = re.compile("^(\d+)$")
        self.RE_MAC_COLON = re.compile(r"^([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})$")
        self.RE_MAC_HYPHEN = re.compile(r"^([0-9a-fA-F]{2}[-]){5}([0-9a-fA-F]{2})$")
        self.RE_MAC_PERIOD = re.compile(r"^([0-9a-fA-F]{4}[\.]){2}([0-9a-fA-F]{4})$")
