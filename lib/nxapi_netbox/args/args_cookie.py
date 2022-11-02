# standard libraries
import argparse

help_save_cookies = 'If present, save cookies.'
help_process_cookies = 'If present, process cookies for the session(s) within a single script invocation.'
help_cookie_file = 'Specifies filname to which cookies will be saved.'
help_disable_urllib_warnings = 'If present, disable urllib3 warnings about insecure connections'

ex_prefix = ' Example(s): '
ex_save_cookies = '{} --save_cookies'.format(ex_prefix)
ex_process_cookies = '{} --process_cookies'.format(ex_prefix)
ex_cookie_file = '{} --cookie_file /tmp/my_cookie_file'.format(ex_prefix)
ex_disable_urllib_warnings = '{} --disable_urllib_warnings'.format(ex_prefix)

ArgsCookie = argparse.ArgumentParser(add_help=False)

mandatory = ArgsCookie.add_argument_group(title='MANDATORY COOKIE ARGS')
default   = ArgsCookie.add_argument_group(title='DEFAULT COOKIE ARGS', description="If absent, a default will be provided")

default.add_argument('--save_cookies',
                     dest='save_cookies',
                     action='store_true',
                     required=False,
                     default=True,
                     help='(default: %(default)s) ' + help_save_cookies + ex_save_cookies)

default.add_argument('--process_cookies',
                     dest='process_cookies',
                     action='store_true',
                     required=False,
                     default=True,
                     help='(default: %(default)s) ' + help_process_cookies + ex_process_cookies)

default.add_argument('--cookie_file',
                     dest='cookie_file',
                     required=False,
                     default=None,
                     help='(default: %(default)s) ' + help_cookie_file + ex_cookie_file)

default.add_argument('--disable_urllib_warnings',
                     dest='disable_urllib_warnings',
                     required=False,
                     action='store_true',
                     default=False,
                     help='(default: %(default)s) ' + help_disable_urllib_warnings + ex_disable_urllib_warnings)

default.set_defaults(loglevel='INFO')
