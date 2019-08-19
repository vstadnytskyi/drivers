"""
DATAQ 4108 device level code

"""
import sys
sys.path.append('//femto/C/All Projects/APS/Instrumentation/Software/Lauecollect')
sys.path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from numpy import nan, mean, std, asarray, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max
from serial import Serial
from time import time, sleep, clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime, time
import logging

from persistent_property import persistent_property
from DB import dbput, dbget
from module_dir import module_dir
from normpath import normpath

from struct import pack, unpack
from timeit import Timer, timeit
from OasisChiller_LL import driver as Oasis_driver #this is DI4108 driver imported from communication LL python file
from circular_buffer_LL import server
from threading import Thread, Timer
import thread
from datetime import datetime

#plt.ion()

__version__ = '0.1.0' #
__date__ = "12-21-17"

class OasisChiller_DL(Thread):

    pr_start_set_temperature = persistent_property('start set temperature', 0.0)
    pr_period = persistent_property('period, s (how often to measure)', 1.0)
    pr_buffer_size = persistent_property('circular buffer size',(1,1))
    
    def __init__(self):
        Thread.__init__(self)

        self.name = 'Oasis_DL'   
        #self.pr_start_set_temperature = 4.0
        #self.pr_period = 10.0
        
        #self.pr_buffer_size = (4,int(86400/self.pr_period))
        self.dev = Oasis_driver() 
        self.queue = ''
        self.RingBuffer = server(size = self.pr_buffer_size, var_type = 'float64')
        self.initialize()
        
        
    def initialize(self):
        self.dev.set_temperature(self.pr_start_set_temperature)
        self.start()
        
        
    def reboot(self):
        self.dev._write('\xFF')
        
        
    def stop(self):
        self.GFlag = False
        self.dev.ser.flushInput()
        self.dev.ser.flushOutput()
        self.reboot()
        self.dev._close_port()
        del self 
        os._exit(1) #uncomment it for the actual run
 
    def set_temperature(self,temperature):
        print('set temperature %r' % temperature)
        self.queue = 'self.dev.set_temperature('+str(temperature)+')'
    
    def status(self): #
        if dev.faults[0]  == 0:
            res = True
        else:
            res = False
        return res #0 is good , 1 is bad

    def exec_queue(self):
        if len(self.queue) != 0:
            exec(self.queue)
            self.queue = ''
            sleep(0.6)

    def run(self):
        """
        This function collects data and puts it in the Ring Buffer.
        It is run in a separate thread(See main priogram)
        """
        print('Measurement thread has started')
        #sleep(10)
        self.dev.ser.readall()
        self.GFlag = True
        data = zeros((4,1))
        while self.GFlag == True:
            tstart = time()
            sleep(0.6)
            self.exec_queue()
            self.set_T = self.dev.get_set_temperature()
            sleep(0.6)
            self.exec_queue()
            self.actual_T = self.dev.get_actual_temperature()
            sleep(0.6)
            self.exec_queue()
            self.faults = self.dev.get_faults()
            data[0,0] = time()
            data[1,0] = self.set_T
            data[2,0] = self.actual_T
            data[3,0] = self.faults[1]
            self.broadcast()
            
            self.RingBuffer.append(data)
            sleep(self.pr_period-(time()-tstart))
                  
        print('thread is done')
    
    def broadcast(self):
        pass
    
    def test1(self):
        for i in range(10):
            pass

def TimeItFunc(string, number):
    arr = zeros(number)
    for i in range(number):
        start_time = clock()
        exec(string)
        arr[i] = clock() - start_time
    print('mean: %.5f \n std: %.5f \n min: %.5f\n max: %.5f' % (mean(arr), std(arr), min(arr), max(arr)))
        
if __name__ == "__main__": #for testing
    dev = OasisChiller_DL()
    print('The Oasis Chiller DL is running')

