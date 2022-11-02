#!/usr/bin/env python3
'''
stc_constants.py
Summary: Constants used by libraries in this repo
Author: Allen Robel
Email: arobel@cisco.com

Description:

Currently, these are used mostly by verify_types.py
'''
class Constants(object):
    def __init__(self):
        self.lib_name = "Constants"

        self.na_bool = False
        self.na_str  = 'na'
        self.na_int  = -1
        self.ipv4_mask_length = 32
        self.ipv6_mask_length = 128
        self.DEFAULT_LOGLEVEL = "INFO"
        self.VALID_LOGLEVELS = ["INFO","WARNING","DEBUG","ERROR","CRITICAL"]
        self.HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')

