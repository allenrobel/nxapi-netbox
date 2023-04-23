#!/usr/bin/env python
"""
Name: log.py
Author: Allen Robel (arobel@cisco.com)
Description: Wrapper for the logger module standardizing log output format.
Synopsis:

   # import convenience function
   from general.log import get_logger

   # create a log instance which will log INFO messages to the console and 
   # DEBUG messages to a rotating logfile /tmp/my_logger_name.log
   log = get_logger('my_logger_name', INFO', 'DEBUG')

Valid logging levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL
"""
import os
import logging
import logging.handlers

our_version = 109


def get_logger(
    _name, _console_level="INFO", _file_level="DEBUG", _capture_warnings=True
):
    """
    returns an instance of <class 'logging.Logger'>
    """
    logging.captureWarnings(_capture_warnings)
    logger = Logger()
    logger.logfile = "/tmp/{}.log".format(_name)
    log = logger.new(_name)
    logger.file_loglevel = _file_level
    logger.console_loglevel = _console_level
    return log


class Logger(object):
    """
    Synopsis:

    from general.log import Logger

    logger = Logger()
    logger.logfile = '/tmp/foobar.log'
    log = logger.new('mylog')
    logger.file_loglevel = 'DEBUG'
    logger.console_loglevel = 'ERROR'
    log.debug('this is a debug log')
    log.error('this is an error log')
    """

    def __init__(self):
        self._loglevel = "INFO"
        self._logfile = "/tmp/logger.log"
        self._levels = dict()
        self._levels["DEBUG"] = logging.DEBUG
        self._levels["INFO"] = logging.INFO
        self._levels["WARNING"] = logging.WARNING
        self._levels["ERROR"] = logging.ERROR
        self._levels["CRITICAL"] = logging.CRITICAL

        self._file_loglevel = self._levels["DEBUG"]
        self._console_loglevel = self._levels["ERROR"]

        self.log = None

    def new(self, _name):
        self.log = logging.getLogger(_name)
        self.log.setLevel(logging.DEBUG)
        self.fh = logging.handlers.RotatingFileHandler(
            self.logfile, maxBytes=10000000, backupCount=3
        )
        self.fh.setLevel(self.file_loglevel)

        self.ch = logging.StreamHandler()
        self.ch.setLevel(self.console_loglevel)

        self.formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(relativeCreated)d.%(lineno)d %(module)s.%(funcName)s %(message)s"
        )
        self.ch.setFormatter(self.formatter)
        self.fh.setFormatter(self.formatter)

        self.log.addHandler(self.ch)
        self.log.addHandler(self.fh)
        return self.log

    @property
    def file_loglevel(self):
        return self._file_loglevel

    @file_loglevel.setter
    def file_loglevel(self, _x):
        if _x.upper() not in self._levels:
            return
        if self.log == None:
            print("Ignored.  call instance.new() first.")
            return
        self._file_loglevel = self._levels[_x.upper()]
        self.fh.setLevel(self._file_loglevel)
        self.log.debug("set file_loglevel to {}".format(_x))

    @property
    def console_loglevel(self):
        return self._console_loglevel

    @console_loglevel.setter
    def console_loglevel(self, _x):
        if _x.upper() not in self._levels:
            print("unknown loglevel {}".format(_x))
            return
        if self.log == None:
            print("Ignored.  call instance.new() first.")
            return
        self._console_loglevel = self._levels[_x.upper()]
        self.ch.setLevel(self._console_loglevel)
        self.log.debug("set console_loglevel to {}".format(_x))

    @property
    def logfile(self):
        return self._logfile

    @logfile.setter
    def logfile(self, _x):
        if self.log != None:
            print(
                "Ignoring. instance.new() was already called.  Call instance.logfile prior to calling instance.new()"
            )
        self._logfile = _x


# class Log(object):
#     '''
#     20180907 - DEPRECATED use get_logger() function in this file (log.py) instead

#     Initialized with a logging level e.g. log = Log("DEBUG").create().

#     By default, loglevel is set to INFO, so the following also works: log = Log().create() if you want to use the default logging level.

#     Valid logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
#     '''
#     def __init__(self, _level='INFO', _format=''):
#         self.valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
#         self._loglevel   = _level.upper()
#         self.version = our_version
#         if self._loglevel not in self.valid_levels:
#             print("Exiting. Invalid logging level {}".format(self._loglevel))
#             os._exit(1)
#         if _format == '':
#             self.format = '%(asctime)s %(levelname)s %(relativeCreated)d.%(lineno)d %(module)s.%(funcName)s %(message)s'
#         else:
#             self.format = log_format
#         self.formatter = logging.Formatter(self.format)
#         self._logfile = None
#         self.log = None

#     @property
#     def loglevel(self):
#         return self._loglevel
#     @loglevel.setter
#     def loglevel(self, _x):
#         if _x.upper() not in self.valid_levels:
#             return
#         if self.log == None:
#             print("Ignored.  call instance.create() first.")
#         print('setting loglevel to {}'.format(_x))
#         self._loglevel = _x.upper()
#         self.log.setLevel(self._loglevel)


#     @property
#     def logfile(self):
#         return self._logfile
#     @logfile.setter
#     def logfile(self, _x):
#         if self.log == None:
#             print("Ignored.  call instance.create() first.")
#             return
#         _fh = logging.FileHandler(_x, mode='a', encoding=None, delay=False)
#         self.log.addHandler(_fh)
#         _fh.setFormatter(self.formatter)


#     def create(self):
#         '''
#         Create a logging instance conforming to proposed CAR log formatting

#         Parameters:
#            level - the desired logging level
#            format - format string (see Python logger documentation)
#                     if format is omitted, the following default string is used:
#                       '%(asctime)s %(levelname)s %(relativeCreated)d.%(lineno)d %(module)s.%(funcName)s %(message)s'

#         Example:

#         myformat = '%(asctime)s %(levelname)s %(message)s'
#         mylevel = 'INFO'
#         log = Log(mylevel, myformat).create()
#         log.info("This is a test")

#         '''
#         #logging.basicConfig(format=self.format)
#         self.log = logging.getLogger("root")
#         self.log.setLevel(self.loglevel)
#         self.log.debug("set loglevel {} on logger {}".format(self.loglevel, "root"))
#         return self.log
