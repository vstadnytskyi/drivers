"""
Oasis Chiller Communication Low Level code 

"""

from numpy import nan, mean, std, asarray, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split
from serial import Serial
from time import time, sleep, clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime
import logging
from persistent_property import persistent_property
from struct import pack, unpack
from timeit import Timer

__version__ = '0.0.1' #
__date__ = "01-11-2018"

class driver(object):

    def __init__(self):
        #tested dec 17, 2017  
        print('bbb')
        self._find_port()
        
        self.ser.flushInput()
        self.ser.flushOutput()
        print("initialization of the driver is complete")
    
    def _find_port(self):
        #this function will scan com ports and find DI-245 devices by sending command A1 and receiving a word 2450 back
        #import serial.tools.list_ports
        #lst = serial.tools.list_ports.comports()
        #print([comport.device for comport in serial.tools.list_ports.comports()])
        for i in range(256):
            com_port = 'COM' + str(i)
            #print('trying ' + com_port)
            try:
                
                self.ser = Serial(com_port, baudrate=9600, timeout=0.1)
                sleep(2)
                try:
                    print('Oasis is found at port %r' % i)
                    if self._inquire('A',3)[0] == 'A':
                        print("the requested device is connected to COM Port %r" % self.ser.port)
                    else:
                        print("Oasis is not found")
                        self.ser.close()
                        print("closing com port")
                except:
                    self.ser.close()
            except:
                pass

        
    
    """Set and Get persistent_property"""
    # functions for persistent properties if needed
    
    """Basic serial communication functions"""   
    def _readall(self):
        #tested dec 17, 2017
        return self.ser.readall()

    def _readN(self,N):
        #tested dec 17, 2017
        data = ""
        if self._waiting()[0] >= N:
            data = self.ser.read(N)
            if len(data) != N:
                print("%r where requested to read and only %N where read" % (N,len(data)))
                data = nan
        else:
            data = nan
        return data
    
    def _write(self,command):
        #tested dec 17, 2017
        self.ser.flushOutput()
        self.ser.write(command)
        
    def _flush(self):
        #tested dec 17, 2017
        self.ser.flushInput()
        self.ser.flushOutput()
        
    def _inquire(self,command, N):
        #tested dec 17, 2017
        self.ser.write(command)
        sleep(0.3)
        while self.ser.inWaiting() != N:
            sleep(0.1)
            
        if self.ser.inWaiting() == N:
            result = self._readN(N)
        else:
            result = nan
        return result
        
    def _waiting(self):
        #tested dec 17, 2017
        return [self.ser.inWaiting(),self.ser.outWaiting()]
        
    def _close_port(self):
        #tested dec 17, 2017
        self.ser.close()


    def _open_port(self):
        #tested dec 17, 2017
        self.ser.open()

    def set_temperature(self,temperature):
        local_byte = pack('h',round(temperature*10,0))
        byte_temp = local_byte[0]+local_byte[1]
        self._inquire('\xe1'+byte_temp,1)
        
        
    def get_set_temperature(self):  
        res = self._inquire('\xc1',3)
        temperature = unpack('h',res[1:3])[0]/10.
        return temperature
        
    def get_actual_temperature(self):
        res = self._inquire('\xc9',3)
        temperature = unpack('h',res[1:3])[0]/10.
        return temperature
    
    def get_faults(self):
        res_temp = self._inquire('\xc8',2)
        res = unpack('b',res_temp[1])[0]
        if res == 0:
            result = (0,res)
        else:
            result = (1,res)
        return result
        
if __name__ == "__main__": #for testing
    dev = driver()
    print('the object dev(port %r) was created. Few test from below can be used.' % dev.ser.port)
    print('dev.get_actual_temperature()')
    print('dev.set_temperature(15)')
    print('dev.get_set_temperature()')
	
