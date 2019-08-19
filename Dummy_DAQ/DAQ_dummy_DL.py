#!/bin/env python
"""
The server DL code for the hierarchical level instrumentation

author: Valentyn Stadnytskyi NIH\LCP
data: Sept 2018 - Nov 2 2018

The server has the basic set of functions:
0) init
1) close
2) abort
3) subscribe (on/off)
4) snapshot
5) task
6)
"""
__version__ = "0.0.0" 
__date__ = "January 20, 2019"

import autoreload3

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


        
class DAQ_dummy_DL(object):
    version = '0.0.'
        
    def __init__(self, name):
        self.name = name
        self.offset = (0,0,0)
        self.buffer_size = (4,7200)

    def help(self,msg_in):
        response = {}
        response['name'] = self.name
        response['controls'] = self.controls.get()
        response['indicators'] = self.indicators.get()
        return response

    def init(self, msg_in):
        debug('device init function is called')
        from numpy import nan
        from time import time
        from circular_buffer_LL import CBServer
        self.controls = Controls()
        self.indicators = Indicators()
        self.indicators.init()
        self.controls.init()
        self.driver.init()

        self.task_queue = []
        
        self.circular_buffer = CBServer(size = self.buffer_size)
        self.controls.offset = (0,0,0)
        self.controls.scanrate = 0.5
        self.controls.running = False
        self.test_lst = [[time()+0,'change_offset',{b'offset':(0,0,0)}],
               [time()+10,'change_offset',{b'offset':(1,1,1)}],
               [time()+10+5,'change_offset',{b'offset':(10,10,10)}],
               [time()+10+10,'change_offset',{b'offset':(50,50,50)}],
               [time()+10+15,'change_offset',{b'offset':(100,100,100)}],
               [time()+10+20,'change_offset',{b'offset':(1,1,1)}]]
        #device.set_task_queue(self.test_lst)
        if not self.controls.running:
            self.start()
        flag = True
        return flag

    def close(self, msg_in = ''):
        return self.stop()

    def abort(self, msg_in = ''):
        return self.reset_task_queue()
    
    def snapshot(self,msg_in = ''):
        from numpy import random
        response = {}
        response['controls'] = self.controls.get()
        response['indicators'] = self.indicators.get()
        return response

    def set_task_queue(self, task_list = []):
        try:
            self.controls.set({b'task_queue':task_list})
            response = True
        except:
            error(traceback.format_exc())
            response = False
        return response
    def reset_task_queue(self):
        try:
            self.controls.set({b'task_queue':[]})
            response = True
        except:
            error(traceback.format_exc())
            response = False
        return response

    def execute_task(self):
        if len(self.controls.task_queue) > 0:
            if self.controls.task_queue[0][0] - time() <=0:
                try:
                    info('executing: %r, with flag %r' %
                         (self.controls.task_queue[0],
                          self.controls.task_queue[0][1] == b'change_offset'))
                    if self.controls.task_queue[0][1] == b'change_offset' or self.controls.task_queue[0][1] == 'change_offset':
                        
                        self.change_offset(self.controls.task_queue[0][2][b'offset'])
                    self.controls.task_queue.pop(0)
                except:
                    pass#error(traceback.format_exc())
                flag = True
            else:
                flag = False
        else:
            flag = False
        return flag
                
            
    def change_offset(self,new_offset):
        debug("new_offset = %r" % new_offset)
        self.controls.set({b'offset':new_offset})

    def acquire_data(self):
        from time import time
        from numpy import random,nan,zeros
        a = time()
        data = self.driver.get_data()
        temp = zeros((4,1))
        temp[0,0] = a
        temp[1,0] = data[0] + self.offset[0]
        temp[2,0] = data[1] + self.offset[1]
        temp[3,0] = data[2] + self.offset[2]
        self.circular_buffer.append(temp)

    def run_once(self):
        try:
            flag = self.execute_task()
            if not flag:
                self.acquire_data()
        except:
            error(traceback.format_exc())
                
    def run(self):
        from time import time
        self.controls.running = True
        while self.controls.running:
            t_start = time()
            self.run_once()
            t_end = time()
            dt = (t_end-t_start)
            if self.controls.scanrate - dt > 0:  
                sleep(self.controls.scanrate- dt)
            else:
                warning('run_once took %r which is more than scanrate %r' %(dt ,self.controls.scanrate))
        self.controls.running = False

    def start(self, msg_in = ''):
        start_new_thread(self.run,())
        return True

    def stop(self, msg_in = ''):
        self.controls.running = False
        return True
        
    def controls(self,msg = {b'all':None}):
        """
        return current control(controls) according to the input dictionary.
        example:
        the command->
        controls(msg = {b'controls':{'button1':None,'button2':None,'scanrate':2.0}})
        will set scanrate to 2.0 and return current setting for button1, button2 and scanrate
        """
        debug('controls command received: %r' % msg)
        response = {}
        err = ''
        if isinstance(msg,dict):
            if b'all' in list(msg.keys()):
                    response = device.controls.get()
            else:
                for key in msg:
                    if msg[key] is None:
                        if key in list(device.controls.get().keys()):
                            response[key] = getattr(device.controls,key.decode("utf-8"))
                        else:
                            response[key] = None
                            err = "control doesn't exist"
                    else:
                        if key in list(device.controls.get().keys()):
                            setattr(device.controls,key.decode("utf-8"),msg[key])
                            response[key] = getattr(device.controls,key.decode("utf-8"))
                        else:
                            response[key] = None
                            err = "control doesn't exist"
            msg_out = {b'controls':response,b'error':err}
        else:
            msg_out = {b'controls':response}
        return msg_out

    def indicators(self, msg = {b'all':None}):
        """
        this function takes 7us to execute probably because of hashtable,etc.
        If I call the function directly, I can execute it in 1 us
        """
        debug('controls command received: %r' % msg)
        response = {}
        err = ''   
        if isinstance(msg,dict):
            if b'all' in list(msg.keys()):
                    response = device.indicators.get()
            else:
                for key in msg:
                    if msg[key] is None:
                        if key in list(device.indicators.get().keys()):
                            response[key] = getattr(device.indicators,key.decode("utf-8"))
                        else:
                            response[key] = None
                            err = "indicator doesn't exist"
                    else:
                        if key in device.controls.get().keys():
                            setattr(device.indicators,key.decode("utf-8"),msg[key])
                            response[key] = getattr(device.indicators,key.decode("utf-8"))
                        else:
                            response[key] = None
                            err = 'error'
            msg_out = {b'indicators':response,b'error':err}
        else:
            msg_out = {b'indicators':response}
        return msg_out


#######
### Test fuctions
########

def snapshot_test():
    port = server.sock.getsockname()[1]
    res = server._transmit(command = 'snapshot', port = port, ip_address = '127.0.0.1')
    return res

def plot_circular_buffer():
    from matplotlib import pyplot as plt
    x = device.circular_buffer.buffer[0,:]
    y1 = device.circular_buffer.buffer[1,:]
    y2 = device.circular_buffer.buffer[2,:]
    y3 = device.circular_buffer.buffer[3,:]
    plt.plot(x,y1,x,y2,x,y3)
    plt.show()

class Indicators(object):
    def __init__(self):
        pass
    
    def init(self):
        self.dict = {}


    def get_pointer(self):
        try:
            response = device.circular_buffer.pointer
        except:
            error(traceback.format_exc())
            response = None
        return response
    pointer = property(get_pointer)

    def get_running(self):
        try:
            response = getattr(device.controls,'running')
        except:
            error(traceback.format_exc())
            response = None #device.controls.running
        return response
    def set_running(self,value):
        setattr(device.controls,'running',value)
    running = property(get_running,set_running)

    def get_current_values(self):
        try:
            response = device.circular_buffer.get_last_N(1)
        except:
            warning(traceback.format_exc())
            response = None
        return response
    current_values = property(get_current_values)

    def get_offset(self):
        try:
            response = device.controls.offset
        except:
            warning(traceback.format_exc())
            response = None
        return response
    offset = property(get_offset)

    def get_lastN(self,N):
        try:
            response = device.circular_buffer.get_last_N(N)
        except:
            warning(traceback.format_exc())
            response = None
        return response


    def get(self, value = None):
        response = {}
        response[b'running'] = self.running
        response[b'offset'] = self.offset
        response[b'pointer'] = self.pointer
        response[b'current_values'] = self.current_values
        if isinstance(value,int):
            response[b'get_lastN'] = self.get_lastN(value)
        else:
            response[b'get_lastN'] = self.get_lastN(device.controls.snapshot_buffer_N)
        return response


        

class Controls(object):
    
    def init(self):
        from numpy import asarray
        self.snapshot_buffer_N = 2

    def get(self):
        response = {}
        response[b'boolean1'] = self.boolean1
        #response[b'boolean2'] = device.driver.boolean2
        #response[b'boolean3'] = device.driver.boolean3
        response[b'scanrate'] = self.scanrate
        #response[b'randfield'] = device.driver.randfield
        #response[b'offset'] = device.offset
        response[b'task_queue'] = self.task_queue
        #response[b'snapshot_buffer_N'] = device.snapshot_buffer_N
        return response

    def set(self,new_controls = {b'temp':False}):
        for key in list(new_controls.keys()):
            setattr(self,key.decode("utf-8"),new_controls[key])
        response = self.get()
        return response

    def get_boolean1(self):
        return device.driver.boolean1
    def set_boolean1(self,value):
        device.driver.boolean1 = value
    boolean1 = property(get_boolean1,set_boolean1)

    def get_task_queue(self):
        return device.task_queue
    def set_task_queue(self,value):
        device.task_queue = value
    task_queue = property(get_task_queue,set_task_queue)

    def get_scanrate(self):
        return device.scanrate
    def set_scanrate(self,value):
        device.scanrate = value
    scanrate = property(get_scanrate,set_scanrate)
    



if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(#filename=gettempdir()+'/communication_LL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    from DAQ_dummy_LL import daq_dummy_driver
    from server_LL import Server_LL

    server = Server_LL('DAQ_dummy_device')
    server.init_server()

    device = DAQ_dummy_DL(name = 'DAQ_dummy_device')
    device.driver = daq_dummy_driver

    #bind server commands and device methods
    server.commands[b'help'] = device.help
    server.commands[b'init'] = device.init
    server.commands[b'snapshot'] = device.snapshot
    server.commands[b'close'] = device.close
    server.commands[b'abort'] = device.abort
    server.commands[b'start'] = device.start
    server.commands[b'stop'] = device.stop
    server.commands[b'indicators'] = device.indicators
    server.commands[b'controls'] = device.controls
    
