#!/bin/env python
"""
The server LL code for the hierarchical level instrumentation

author: Valentyn Stadnytskyi NIH\LCP
date: Jan 2019

The very simple Data Acquisition simulator.
It has 3 channels that generate random data arround offset
there are 3 booleans that can turn on and off the data production.

"""
__version__ = "0.0.0" 
__date__ = "January 20, 2019"

#import autoreload3

import traceback
import psutil, os
import platform #https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
p = psutil.Process(os.getpid()) #source: https://psutil.readthedocs.io/en/release-2.2.1/
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITYsindows':
if platform.system() == 'Windows':
    p.nice(psutil.NORMAL_PRIORITY_CLASS)
elif platform.system() == 'Linux':
    p.nice(0) # nice runs from -20 to +12, where -20 the most not nice code(highest priority)


from numpy import nan, mean, std, nanstd, asfarray, asarray, hstack, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max
from time import time, sleep, clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime, time
from logging import debug,info,warning,error

###These are Friedrich's libraries.
###The number3 in the end shows that it is competable with the Python version 3.
###However, some of them were never well tested.
if sys.version_info[0] ==3:
    from persistent_property3 import persistent_property
    from DB3 import dbput, dbget
    from module_dir3 import module_dir
    from normpath3 import normpath
    ###In Python 3 the thread library was renamed to _thread
    from _thread import start_new_thread
else:
    from persistent_property import persistent_property
    from DB import dbput, dbget
    from module_dir import module_dir
    from normpath import normpath
    from thread import start_new_thread

from struct import pack, unpack
from timeit import Timer, timeit

from datetime import datetime

from precision_sleep import precision_sleep #home-built module for accurate sleep

import msgpack
import msgpack_numpy as m
import socket

import platform
from numpy import nan
server_name = platform.node()


        
class DAQ_dummy_LL(object):
    version = '0.0.0'
        
    def __init__(self, name):
        self.name = name
        self.randfield = (1024,1024,1024)
        self.boolean1 = True
        self.boolean2 = True
        self.boolean3 = True
        self.connected = False

    def init(self):
        
        self.connect()
        return True

    def connect(self):
        self.connected = True
                
            
    def set_offset(self,new_offset):
        debug("new_offset = %s" % str(new_offset))
        self.offset = new_offset
        
    def get_offset(self):
        return self.offset
    offset = property(get_offset,set_offset)
    

    def get_data(self, points = 1):
        from numpy import random,nan,zeros
        temp = zeros((3,points))
        for i in range(points):
            if self.boolean1 and self.connected:
                b = random.randint(self.randfield[0])
            else:
                b = nan

            if self.boolean2 and self.connected:
                c = random.randint(self.randfield[1])
            else:
                c = nan

            if self.boolean3 and self.connected:
                d = random.randint(self.randfield[2])
            else:
                d = nan
            temp[0,i] = b
            temp[1,i] = c
            temp[2,i] = d
        return temp
 

    
   
daq_dummy_driver = DAQ_dummy_LL(name = 'daq_dummy_driver')




if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(#filename=gettempdir()+'/communication_LL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    self = daq_dummy_driver
    #device.indicators.running = False
