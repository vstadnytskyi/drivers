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
import pdb
from persistent_property import persistent_property

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
    saved_position = persistent_property('saved_position', 0)
    
    def __init__(self, name = 'Test Cube'):
        #controllers can be T or K - cubes. This has to be specified because different controllers have different sequence of bytes for the same command
        self.name = name
        
    def init(self):
        """find the port to which the motor is connected. FIXIT: implement this function"""
        pass
        return False

    def stop(self):
        """performs orderly shut down of this motor:
             - stops serial port communication
             - destroys instance
             FIXIT
            """
        
        return False
    
    def home(self, go_to_saved = False):
        """ homes the motor. return current posotion. Will go to saved position if go_to_saved is True.
            FIXIT: implement this function"""
        try:
            pass
        except:
            pass
    
    
    
    def set_settings(self):
        """set persistent property first time (Note, it will rewrite existing persistent property file"""
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


    def get_position(self):
        """gets current position. the function checks if requested command is executable. If yes, return value. If not, return nan and an error message."""
        try:
            result = self.dev._get_position()
        except:
            self.error = 'failed to get position'
            result = nan
        return result

    def set_position(self,value):
        """sets current position to specified value. the function checks if requested command is executable. If yes, return value. If not, return nan and an error message."""
        try:
            self.dev._set_position(value)
            result = self.dev._get_position()
        except:
            self.error = 'failed to set position'
            result = nan
        return result

    def moveAbs(self,new_pos): #value in um
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


if __name__ == "__main__":
   self = motion_controller(name = "Test Cube")
