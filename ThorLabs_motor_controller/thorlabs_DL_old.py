#!/bin/env python
"""
ThorLabs TDC001 and KDC001 cubes Device Level code.

author: Valentyn Stadnytskyi
valentyn.stadnytskyi@nih.gov

The communication protocols: 
https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf issue 20
"""

__version__ = 0.1 #under restructioning
from time import sleep, time
from numpy import zeros, ones, mean, std, sign, nan
from serial import Serial
from struct import pack, unpack
from ThorLabs_controller_LL import Cube as cube
import pdb
from persistent_property import persistent_property
"""
Create config file with parameters for different motors.
"""

class motion_controller(object):
    
    serial_number = persistent_property('serial_number', 0000000000)
    location = persistent_property('location', '0-0')
    mnemonic_name = persistent_property('mnemonic_name','')
    physical_name = persistent_property('physical_name','')
    motor = persistent_property('motor', 'None')
    controller = persistent_property('controller', 'None')
    soft_limits = persistent_property('soft_limits', (nan,nan)) #in mm
    gear = persistent_property('gear', nan)
    counts_per_revolution = persistent_property('counts_per_revolution',nan)
    backlash = persistent_property('backlash',nan)
    backoff = persistent_property('backoff',nan)
    last_known_position  = persistent_property('last_known_position',nan)
    pitch = persistent_property('pitch',nan)
    pitch_units = persistent_property('pitch_units','')
    
    def __init__(self, port = None):
        #controllers can be T or K - cubes. This has to be specified because different controllers have different sequence of bytes for the same command
        self.dev = cube(port,motor = 'T', controller = 'T')
        
        self.get_settings()
    def identify(self):
        self.dev._identify()
    def set_settings(self):
        """this function gets setting from a file(or somewhere else)
        and apply them to this motor. The function will identify the motor by its'
        serial number and assigned values from the table"""
        self.physical_name = 'Test Motor'
        self.serial_number = '83000000'
        self.location = '2-5'
        self.motor = 'T'
        self.controller = 'T'
        self.soft_limits = (0,205824)
        self.gear = 67
        self.counts_per_revolution = 512
        self.backlash = 3000
        self.backoff = 0
        self.last_known_position = 0
        self.pitch = 1000
        self.pitch_units = 'um'
        self.direction = sign(self.backlash) #stands for positive
        self.description = 'This is Description'
    
    
    
    
    
    
    
    def show_setting(self):
        """
        this command will print current settings for this mottor
        
        """
        print('Physical Name %r' % self.physical_name )

    def moveRel(self,RelMove): #value in steps
        print('Moving relative by %r' % RelMove)
        CurPos = self.dev._get_position()
        self.moveAbs(CurPos + RelMove)

        
    def moveAbs(self,NewPos): #value in um
        flag = False
        response_str = None
        if NewPos > self.soft_limits[1] or NewPos < self.soft_limits[0]:
            flag = False
            response_str = 'out of soft limits'
        else:    
            if self.controller == 'K':
               print('moving motor %r connected to the %r cube' % (self.motor, self.controller))

            if self.controller == 'T':
                flag = False
                print('moving motor %r connected to the %r cube' % (self.motor, self.controller))
                print('number of steps to move absolute = %r' % NewPos)
                CurPos = self.get_position()
                if (NewPos - CurPos)*sign(self.backlash) > 0: 
                    self.dev._moveAbs(NewPos)
                elif (NewPos - CurPos)*sign(self.backlash) < 0:
                    self.dev._moveAbs(NewPos-self.backlash)
                    self.dev._moveAbs(NewPos-self.backlash) 
                else:
                    pass
            if self.dev._get_position() == NewPos:
                flag = True
                response_str = 'move is complete'
        return flag, response_str
    
    
    def get_position(self):
        return self.dev._get_position()
    
    def set_position(self,value):
        self.dev._set_position(value)
        return self.dev._get_position()

    def home(self):
        return self.dev._home()

    def run_test1(self,N):
        from random import random

        for i in range(N):
            start = time()
            goto = int(random()*6*512.*67.)
            self.moveAbs(goto)
            arrived = self.get_position()
            print [time()-start,goto,arrived]

            
if __name__ == "__main__":
    print('dev = motion_controller()')
    print('dev.identify()')
    print('dev.moveRel(1000)')
    print('dev._blink()')
    print('dev.get_position()')
    print('dev._moveAbs(0)')
    print('dev.run_test1(2)')
