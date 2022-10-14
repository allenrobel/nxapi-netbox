#!/usr/bin/env python3
'''
Name: nxapi_config.py
Author: Allen Robel (arobel@cisco.com)
Description: Classes containing methods for retrieving the output of 'show' CLI from an NXOS switch via nxapi 

Synopsis:

from general.log import get_logger
from nxapi.nxapi_show import NxapiShow

script_name = 'my_script'
log = get_logger(script_name, 'INFO', 'DEBUG')

s = NxapiShow('admin','password','10.1.1.1', log)
# nxapi_init() can take an argparse instance to alter cookie and urllib3 behavior. 
# By default, cookies are enabled.
# see ./lib/args/args_cookie.py for details
s.nxapi_init()
s.cli = 'show clock'
# s.show() sends s.cli to the switch, retrieves the response, and stores it in a dict() s.op (op stands for output)
s.show()
# s.body[0] will be a dict() containing something similar to: {'simple_time': '13:20:33.847 PDT Mon Sep 03 2018\n'}
print('the time is {}'.format(s.body[0]['simple_time']))
'''
our_version = 102

from nxapi.nxapi_base import NxapiBase

class NxapiShow(NxapiBase):
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
