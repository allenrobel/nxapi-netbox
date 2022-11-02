#!/usr/bin/env python3

"""
Name: util.py
Contributors:
   Allen Robel (arobel@cisco.com) - original code
   Stefaan Lippen (for fname() fcaller() @ http://stefaanlippens.net/python_inspect)
   Arron Hall (merge_dicts()) @ https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression#26853961

Summary: Utility classes and methods for for dssperf scripts.

Detail: TODO: Fill this in for each function added to this library

   Currently provides a wrapper around "print" to add the following methods
   - d(msg) if verbose is true, print msg ("d" stands for "debug")
   - c(msg) unconditionally print msg     ("c" stands for "comment")
   - q  a dequeue object into which the last 30 messages are stored.  Can be popped
     with e.g. q.pop() and appended to with e.g. q.append(thing)

Usage:

   echo = Echo(verbose)   # where verbose is either True or False
   echo.c("This will be printed with a timestamp unconditionally")
   echo.d("This will be printed with a timestamp only if cfg.verbose is True")
   echo.p()    # This will print the last 30 messages from both echo.c and echo.d
               # Normally placed at the end of a script, or as part of an abort handler

"""
our_version = 141
# standard libraries
import time  # localtime(), strftime()
from collections import deque
import inspect # inspect.stack()
import json    # read_json()
import os
import re
import random, string
import sys
# local libraruies
from nxapi_netbox.general.verify_types import VerifyTypes # Timer()


class NxTimer(object):
    '''NX-OS timer conversions'''
    def __init__(self,timer='0:0:0'):
       self.timer = timer
       self.timer2sec = 0.0
       self.seconds = 0.0
       self.minutes = 0.0
       self.hours   = 0.0
       self.days    = 0.0
       self.weeks   = 0.0
       self.unit2sec = dict()
       self.unit2sec['s'] = 1.0
       self.unit2sec['m'] = self.unit2sec['s'] * 60.0
       self.unit2sec['h'] = self.unit2sec['m'] * 60.0
       self.unit2sec['d'] = self.unit2sec['h'] * 24.0
       self.unit2sec['w'] = self.unit2sec['d'] * 7.0
       self.unit2sec['M'] = self.unit2sec['w'] * 4.0
 
       # seconds.milliseconds e.g. 9.1232
       self.re_sms = re.compile('^.*?(\d+)\.(\d+).*?$')
       #                               10:5:23
       self.re_hms = re.compile('^.*?(\d+):(\d+):(\d+).*?$')
       #                                6d12h
       self.re_dh  = re.compile('^.*?(\d+)d(\d+)h.*?$')
       #                   1w0d
       self.re_wd  = re.compile('^.*?(\d+)w(\d+)d.*?$')

    # not using in this Class  This returns the product of a list
    def prod_seq(seq):
        if len(seq) == 0:
            return
        prod = seq.pop()
        while len(seq) > 0:
            prod *= seq.pop()
        return prod

    def refresh(self,timer):

       m_sms = self.re_sms.search(timer)
       if m_sms:
           self.timer2sec = 0.0
           self.seconds = float(m_sms.group(1))
           self.milliseconds = float(m_sms.group(2))
           self.timer2sec = float('{}.{}'.format(m_sms.group(1),m_sms.group(2)))
           return
       m_hms = self.re_hms.search(timer)
       if m_hms:
           self.timer2sec = 0.0
           self.weeks   = 0.0
           self.days    = 0.0
           self.hours   = float(m_hms.group(1))
           self.minutes = float(m_hms.group(2))
           self.seconds = float(m_hms.group(3))
           self.timer2sec += self.hours   * self.unit2sec['h']
           self.timer2sec += self.minutes * self.unit2sec['m']
           self.timer2sec += self.seconds * self.unit2sec['s']
           return
       m_dh = self.re_dh.search(timer)
       if m_dh:
           self.timer2sec = 0.0
           self.days = float(m_dh.group(1))
           self.hours = float(m_dh.group(2))
           self.timer2sec += self.days  * self.unit2sec['d']
           self.timer2sec += self.hours * self.unit2sec['h']
       m_wd = self.re_wd.search(timer)
       if m_wd:
           self.timer2sec = 0.0
           self.weeks = float(m_wd.group(1))
           self.days  = float(m_wd.group(2))
           self.timer2sec += self.weeks * self.unit2sec['w']
           self.timer2sec += self.days  * self.unit2sec['d']
       
class Timer(object):
    '''Timer which tracks last/min/max/avg/total elapsed time between start() and stop() calls

      Takes two arguments:

      1. log instance - mandatory
      2. the queue length for the last N samples.  Optional. Default is 10 samples.

      Synopsis:

      script_name = 'myscript'
      console_log_level = 'INFO'
      file_log_level = 'DEBUG'
      log = get_logger(script_name, console_log_level, file_log_level)

      Example 1:

      t = Timer(log)
      t.start()
      time.sleep(4)
      t.stop()
      print('{} elapsed time'.format(t.elapsed))

      Example 2:

      t = Timer(log, 15)
      t.start()
      time.sleep(5)
      t.stop()
      t.start()
      time.sleep(18)
      t.stop()
      print("last sample {} average duration {} max duration {} sum of all durations {}".format(t.last,
                                                                                                 t.avg,
                                                                                                 t.max,
                                                                                                 t.elapsed)
      print("Clearing all timer state and statistics")
      t.clear()

    '''
    def __init__(self,log, qlen=10):
        self.lib_name = "Timer"
        self.lib_version = our_version
        self.log_prefix = '{}_{}'.format(self.lib_name, self.lib_version)
        self.log = log
        self.verify = VerifyTypes(self.log)

        if not self.verify.is_int(qlen):
            self.log.warning("invalid timer sample queue length {}.  Setting to default 10".format(qlen))
            qlen = 10


        self.qlen         = int(qlen)
        self._running     = False
        self.time_start   = 0.0
        # duration between lastest start/stop interval
        self.time_last    = 0.0
        self.time_total   = 0.0
        # total of all time between start/stop intervals
        self.time_elapsed = 0.0
        self.time_max     = 0.0
        self.time_min     = 9999999990.0
        self.time_avg     = 0.0
        self.q = deque(maxlen=self.qlen)

    @property
    def running(self):
        return self._running
    @running.setter
    def running(self, _x):
        if not self.verify.is_boolean(_x):
            self.log.error("Exiting. Expected boolean. Got {}".format(_x))
        self._running = _x

    def start(self):
        if self._running:
            return
        self.time_start = time.time()
        self.running = True

    def stop(self):
        if not self._running:
            return
        self.running = False
        self.time_last = (time.time() - self.time_start)
        self.q.append(self.time_last)
        # q will be at least 1 at this point so below is safe
        self.time_avg = sum(self.q) / len(self.q)
        self.time_total += self.time_last
        self.time_elapsed = self.time_last
        if self.time_last > self.time_max:
            self.time_max = self.time_last
        if self.time_last < self.time_min:
            self.time_min = self.time_last

    @property
    def total(self):
        return self.time_total
    @property
    def elapsed(self):
        '''
        the time period between each start() and stop() call
        '''
        return self.time_elapsed
    @property
    def max(self):
        '''
        the maximum elapsed time seen since the timer was created or cleared
        '''
        return self.time_max
    @property
    def min(self):
        '''
        the minimum elapsed time seen since the timer was created or cleared
        '''
        return self.time_min
    @property
    def avg(self):
        '''
        the average elapsed time seen since the timer was created or cleared
        this is a rolling average, averaged over the entries in the q
        '''
        return self.time_avg
    @property
    def last(self):
        '''
        the last elapsed time between start() and stop() calls
        '''
        return self.time_last
    def clear(self):
        self.time_start   = 0.0
        self.time_elapsed = 0.0
        self.time_last    = 0.0
        self.time_avg     = 0.0
        self.time_min     = 9999999.0
        self.q.clear()

class Constants(object):
    '''Provides constants for common values e.g. na_bool, na_str, na_int

      na_bool - if False, then the value is not applicable i.e. invalid
                if True, the value is valid
      na_str  - if 'na', then the value is not applicable i.e. invalid
                if any other string, the value is valid
      na_int  - if -1, then the value is not applicable i.e. invalid
                if any other integer, the value is valid
      HEX_DIGITS - compare a string as follows
                   from util import Constants
                   my_string = 'ea3f'
                   c = Constants()
                   c.HEX_DIGITS.issuperset(my_string)
                      True <<<<<
                   my_string = 'z8r8'
                   c.HEX_DIGITS.issuperset(my_string)
                      False <<<<<

    '''
    def __init__(self,level="INFO"):
        self.na_bool = False
        self.na_str  = 'na'
        self.na_int  = -1
        self.HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')
    def is_hex(self,_value):
        if self.HEX_DIGITS.issuperset(_value):
            return True
        else:
            return False

# functions

def ranges(ints):
    '''
    generator which, given a list of integers, yields tuples comprising 
    the start and end of each contiguous range within the list

    For example, when called with the following list:

        ranges([1,4,39,5,2,7,8,9,10])

    yield the following tuples:

    (1, 2)
    (4, 5)
    (7, 10)
    (39, 39)
    '''
    ints = sorted(set(ints))
    range_start = previous_number = ints[0]
    for number in ints[1:]:
        if number == previous_number + 1:
            previous_number = number
        else:
            yield range_start, previous_number
            range_start = previous_number = number
    yield range_start, previous_number

def split_list(l,n):
    '''
    splits list l into n sublists.
    The number of elements in l must be evenly divisible by n (we don't error check anything)

    Example:

        list1 = [1,2,3,4]
        list2 = split_list(list1,2)

        list2 is now [[1,2],[3,4]]
    '''
    return [l[i:i+n] for i in range(0, len(l), n)]

# if sys.version < '3':
#     def b(x):
#         return x
# else:
#     import codecs
#     def b(x):
#         return codecs.latin_1_encode(x)[0]

def list2options(l):
    '''
    Convenience method to present items in a list as choices in standard [item1 | item2 | item3] format.

    Usage:

    choices = ['choice1','choice2','choice3']
    print "Your choices are %s" % (list2options(choices),)

    Will print the following:

    Your choices are [choice1 | choice2 | choice3]
    '''
    return '[%s]' % ' | '.join(item for item in l)


def fname():
    '''
    Return the name of the currently executing function from within that function

    Usage:
       def foo():
           print('{} some comment').format(fname())
    '''
    return inspect.stack()[1][3]

def fcaller():
    '''
    Return the name of the calling function
    '''
    return inspect.stack()[2][3]

def file_exists(fn):
    if os.path.exists(fn):
        return True
    return False

def is_file(fn):
    if os.path.isfile(fn):
        return True
    return False

def sanity_check_file(fn):
    if not file_exists(fn):
        print("Exiting. File does not exist: {}".format(fn))
        exit(1)
    if not is_file(fn):
        print("Exiting. Is not a file: {}".format(fn))
        exit(1)

# def get_cfg_from_file(fn):
#     '''
#     DEPRECATED: Use file2list() instead
#     Given a file, fn, return lines in fn as a list with one line per list element.
#     '''
#     sanity_check_file(fn)
#     cfg = open(fn).read().splitlines()
#     return cfg

def read_json(fn):
    sanity_check_file(fn)
    try:
        with open(fn, 'r') as fh:
            _json = json.load(fh)
    except:
        print('Exiting. Unable to load file {}'.format(fn))
        exit(1)
    return _json

def file2list(fn,clean=False):
    '''
    Given a file, fn, return lines in fn as a list with one line per list element.  Sanity-checking is done to make sure fn exists and is a file.

    Arguments:
       fn - path to the file
       clean - Defaults to False
            If True, strip blank lines '^\s*$' and lines beginning with comments '^\s*#'
            If False, file will be returned with blank lines and comments intact

    Examples:

        my_list = file2list(my_file)
            my_list will contain all contents of my_file, each line in a separate list element
        my_list = file2list(my_file, clean=False)
            same as previous example
        my_list = file2list(my_file, clean=True)
            my_list will contain only lines from my_file that don't contain comments and are not blank
    '''
    sanity_check_file(fn)
    cfg = open(fn).read().splitlines()
    if clean is False:
        return cfg
    rc_comment = re.compile('^\s*#')
    rc_blank   = re.compile('^\s*$')
    cleaned = []
    for line in cfg:
        if not rc_blank.search(line) and not rc_comment.match(line):
            cleaned.append(line)
    return cleaned

# def get_duts_from_file(fn):
#     '''
#     Given a file, fn, with one IP/hostname per line, return list of IP/hostname contained in fn
#     '''
#     sanity_check_file(fn)
#     with open(fn,'r') as fh:
#         duts = fh.readlines()
#     dut_list = []
#     for dut in duts:
#         test = dut.splitlines()
#         for line in test:
#             line.strip()
#             if line and not "#" in line:
#                 dut_list.append(line)
#     return dut_list

# def get_dutlist(dut,fn):
#     '''return a dutlist, from --dut and --hostfile options (see cargs.py)'''
#     if dut == 'file':
#         dutlist = get_duts_from_file(fn)
#     else:
#         dutlist = re.split(",", str(dut))
#     return dutlist

def timestamp():
    return time.strftime("%Y%m%d_%H:%M:%S", time.localtime())

# class Echo:
#     def __init__(self,verbose=False):
#        self.verbose = verbose
#        self.q = deque(maxlen=30)
#        self.version = 104

#     def time_prepend(fn):
#         def wrapped(self,msg):
#             return fn(self,time.strftime("%Y%m%d %H:%M:%S", time.localtime()) + " " + msg)
#         return wrapped

#     @time_prepend
#     def d(self,msg):
#         self.q.append(msg)
#         if(self.verbose):
#             print(msg)

#     @time_prepend
#     def c(self,msg):
#         self.q.append(msg)
#         #print msg

#     def p(self,source=''):
#         '''
#         Pop the queue of last 30 messages accumulated within the instance of Echo
#         by the comment c() and debug d() methods
#         An optional source string can be passed so that the queue can be identified by the end user

#         Example:
#             echo = Echo()
#             echo.p("myScript")
#         '''
#         prefix = " popqueue(" + str(self.version) + ") "
#         if source != '':
#             source = " from " + source
#         print("-------------------------------------------------------------------------")
#         print("{} {} {}".format( prefix,"30 most recent cli",source))
#         print("-------------------------------------------------------------------------")
#         for item in self.q:
#             print("{}".format(item))
#         print("-------------------------------------------------------------------------")

def counter(start=0, step=1):
    '''Increment each time called.

    Usage:
     
       c = counter()
       print c() - prints 1
       print c() - prints 2
       print c() - prints 3
       etc

      c = counter(0,4)
      print c() - prints 4
      print c() - prints 8
      print c() - prints 12
      etc
    '''
    x = [start]
    def _inc():
        x[0] += step
        return x[0]
    return _inc

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    From Aaron Hall: https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression#26853961
    """
    result = {}
    for d in dict_args:
        result.update(d)
    return result

def randomword(length):
    rand = ''.join(random.choice(string.ascii_lowercase) for i in range(length))
    rand += ''.join(random.choice(string.ascii_uppercase) for i in range(length))
    rand += ''.join(random.choice(string.digits) for i in range(length))
    rand += ''.join(random.choice(string.punctuation) for i in range(length))
    return ''.join(random.choice(rand) for i in range(length))

class ZippedIterator(object):
    '''
    zip() n list() and iterate over the result.

    return type: iterator which yields tuple()

    Synopsis

    A = [1,2,3]
    B = [4,5,6]
    ...
    N = [n1,n2,n3]

    z = ZippedIterator([A, B, ..., N])
    i = z.items
    foo = next(i)  # [1,4,...,n1]
    foo = next(i)  # [2,5,...,n2]
    foo = next(i)  # [3,6,...,n3]
    foo = next(i)  # Stop iteration error

    Example

    from util import ZippedIterator
    A = [1,2,3]
    B = [4,5,6]
    C = [7,8,9]
    D = [10,11,12]
    z = ZippedIterator([A, B, C, D])
    i = z.items
    while True:
        try:
            print(next(i))
        except:
            break

    Output:

    (1, 4, 7, 10)
    (2, 5, 8, 11)
    (3, 6, 9, 12)

    '''
    def __init__(self, T):
        for L in T:
            if type(L) != type(list()) and type(L) != type(tuple()):
                print('exiting. expected list() or tuple().  Got {}'.format(L))
        self.zipped = zip(*T)

    @property
    def items(self):
        while True:
            try:
                yield next(self.zipped)
            except Exception as e:
                break

class NestedIterator(object):
    '''
    nested iteration over two list()
    return type: iterator which yields tuple()

    Synopsis

    A = [1,2,3]
    B = [4,5,6]
    n = NestedIterator(A, B)
    i = n.items

    foo = next(i)  # [1,4]
    foo = next(i)  # [1,5]
    foo = next(i)  # [1,6]
    foo = next(i)  # [2,4]
    ...
    foo = next(i)  # Stop iteration error

    Example

    A = [1,2]
    B = [1,2,3,4]
    n = NestedIterator(A, B)
    i = n.items
    while True:
        try:
            print(next(i))
        except:
            break
    
    Output

    [1, 1]
    [1, 2]
    [1, 3]
    [1, 4]
    [2, 1]
    [2, 2]
    [2, 3]
    [2, 4]

    '''
    def __init__(self, A, B):
        if type(A) != type(list()) and type(A) != type(tuple()):
            print('exiting. expected list() or tuple() for A.  Got {}').format(A)
        if type(B) != type(list()) and type(B) != type(tuple()):
            print('exiting. expected list() or tuple() for B.  Got {}').format(B)
        self._A = A
        self._B = B

        def _get():
            for a in A:
                for b in B:
                    yield((a,b))
        self.i = _get()

    @property
    def items(self):
        while True:
            try:
                yield next(self.i)
            except Exception as e:
                break
