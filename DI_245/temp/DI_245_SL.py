#!/bin/env python

"""
DI-245 Data Acquisition Unit server (Server level code)

Valentyn Stadnytskyi, Oct 2017 - Nov 2017
"""

#This server has 2 threads: 
#'-> Thread_Server: for communication 
#'-> Thread_Measurements: for collection data from the DI-245 module

# 
# self.server_command_dict[0] = 'init'
# self.server_command_dict[1] = 'close'
# self.server_command_dict[2] = 'broadcast fixed rate'
# self.server_command_dict[3] = 'request average of N'
# self.server_command_dict[4] = 'request buffer all'
# self.server_command_dict[5] = 'request buffer update'
# 
# self.server_command_dict[6] = 'perform calibration'
# self.server_command_dict[7] = 'get calibration' #stores up to 5 calibration records, if requested older than 5 or it doesn't exist the last one will be performed. 

import msgpack
import msgpack_numpy as m
from threading import Thread
import thread
from socket import *
from Queue import Queue
from time import time,sleep
import DI_245_DL
import numpy as np
from serial import Serial
import datetime
import sys
import os.path
import matplotlib.pyplot as plt
from pdb import pm
from struct import pack
import wx
import sys
import StringIO
import circular_buffer_LL
import logging
from logging import error,warn,info,debug
logging.basicConfig(filename='di_245_SL.log', level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    

__version__ = "1.0.3" # cleaned code. fix problem with not-wrapping around.
__date__ = "11-05-17"

SerialNumber = '57D81C13'


sleep(0.1) #I don't know if this is important.

DEBUG = False

dev = DI_245_DL.DI245_DL(SN = SerialNumber)

class ServerSocket(Thread): 
    def run(self):
        #read variable "a" modify by thread 2
        print 'Attempting to start server on port 9900..'
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('', 9910)) 
        self.sock.listen(5) 
        
        print 'Server is now listening on port 9900!'
        self.server_command_dict = {}
        self.server_command_dict[0] = 'init'
        self.server_command_dict[1] = 'close'
        self.server_command_dict[2] = 'broadcast fixed rate'
        self.server_command_dict[3] = 'request average of N'
        self.server_command_dict[4] = 'request buffer all'
        self.server_command_dict[5] = 'request buffer update'
        self.server_command_dict[6] = 'perform calibration'
        self.server_command_dict[7] = 'get calibration' #stores 1 oldest calibration record.
        self.server_command_dict[8] = 'save to a file'
        
        msg_in = [-1,-1,-1,-1]
        gflag = True
        while gflag:
            self.client, self.addr = self.sock.accept()
            self._log_last_call()
            info( 'Client has connected: %r %r' % (self.client, self.addr ))
            pointer_temp = dev.buffer.pointer
            msg_in = msgpack.unpackb(self.client.recv(64),object_hook=m.decode)
            info('input from the client: %r' % msg_in)
  
            if msg_in[0] == 0:
                self._send([msg_in[0],time(),'server is working',-1])
            elif msg_in[0] == 1:
                self._send([msg_in[0],time(),'Termination of the server initated',-1])
                del self
                dev.full_stop()
                gflag = False    
            elif msg_in[0] == 2:
                self._send([msg_in[0],time(),'broadcast on demand request executed',-1])
                dev.broadcast(method = "on demand")
            elif msg_in[0] == 3:
                self._send([msg_in[0],time(),np.mean(dev.buffer.get_last_N(N = int(msg_in[1])),axis = 1),np.std(dev.buffer.get_last_N(N = int(msg_in[1])), axis = 1)])
            elif msg_in[0] == 4:
                self._send([msg_in[0],time(),pointer_temp,dev.buffer.get_all()])
            elif msg_in[0] == 5 and msg_in[1] != '':
                if pointer_temp>msg_in[1]:
                    temp_n = pointer_temp-msg_in[1]
                else:
                    temp_n = dev.buffer.size[1]+pointer_temp-msg_in[1]
                self._send([msg_in[0],time(),pointer_temp,dev.buffer.get_last_N(N = temp_n)])        
            elif msg_in[0] == 6:
                dev.set_calib()
                self._send([msg_in[0],time(),dev.calib,-1])
            elif msg_in[0] == 7:
                self._send([msg_in[0],time(),dev.calib,-1])    
            elif msg_in[0] == 8:
                self._send([msg_in[0],time(),'command is not assigned yet: not decided yet ',-1])
            elif msg_in[0] == 9:
                self._send([msg_in[0],time(),'command is not assigned yet: not decided yet',-1])    
            else:
                self._send([msg_in[0],time(),'do not know how to interpret msg_in[0] is not an integer',-1])

                
    def _receive(self):
        return self.client.recv(64)
    
    def _send(self,msg_out):
        msg = msgpack.packb(msg_out, default=m.encode)
        sleep(0.025)
        length = str(len(msg))
        self.client.sendall(length)
        sleep(0.025)
        self.client.sendall(msg)
        
    def _log_last_call(self):
        self.log_last_client = self.client       
        self.log_last_addr = self.addr       
        

class thread_measurements(Thread):
    def run(self):
        dev.start_scan()
        sleep(3)
        brdcst_time_start = time()
        while True:
            while dev.ser.inWaiting()>3:
                dev.buffer.append(dev.read_number())
            if time() - brdcst_time_start > 1:
                dev.broadcast(method = "on demand")
                brdcst_time_start = time()
                info('Current ring buffer pointer %r' % dev.buffer.pointer)
            sleep(0.02)

if __name__ == "__main__":      
    thread_measurements().start()
    ServerSocket().start()
    print "threads started"

