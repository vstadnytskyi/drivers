#!/bin/env python
"""
ThorLabs TDC001 and KDC001 cubes Device Level code

Valentyn Stadnytskyi
valentyn.stadnytskyi@nih.gov

The communication protocols: 
https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf issue 20
"""
from time import sleep, time
from numpy import zeros, ones, mean, std, sign
from serial import Serial
from struct import pack, unpack
import pdb
"""
Create config file with parameters for different motors.
"""
port = 'COM9'
class motion_controller(object):
    def __init__(self, port):
        #controllers can be T or K - cubes. This has to be specified because different controllers have different sequence of bytes for the same command
        self.port = port

        self.ser = Serial(self.port, baudrate=115200, bytesize = 8, parity='N', stopbits=1, timeout=1)
        self.get_settings()
        ##Motor Parameters for Z806

        #this will turn on message to be send upon completion of the move.
        self.ser.write(pack('BBBBBB',0x6C,0x04,0x00,0x00,0x80,0x01))
        #suspend end of motion message
        #self.ser.write(pack('BBBBBB',0x6B,0x04,0x00,0x00,0x21,0x01))
        """MGMSG_HW_NO_FLASH_PROGRAMMING"""
        #self.ser.write()
        
    def get_settings(self):
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
        self.last_know_position = 0
        
        self.pitch = 1000
        self.pitch_units = 'um'

        self.direction = sign(self.backlash) #stands for positive

        self.description = 'This is Description'
    def show_setting(self):
        """
        this command will print current settings for this mottor
        
        """
        print('Physical Name %r', )
    def _read(self):
        string = ''
        while self.ser.in_waiting >0:
            string += self.ser.read()
        return string

    def _write(self,command):
        self.ser.write(command)

    def _inquiry(self,command, length = None):
        self.ser.write(command)
        if length == None:
            sleep(0.1) #I don't know if this is necessery
        else:
            t = time()
            while self.ser.in_waiting < length:
                sleep(0.1)
        return self._read()
    def _waiting(self):
        return [self.ser.in_waiting,self.ser.out_waiting]
    
    def _unpack(self,var,f,t):
        return unpack('B'*len(var[f:t+1]),var[f:t+1])
    def byte_to_int(self,var):
        result = 0
        for i in var:
            integer = integer + 2*2

    def _blink(self):
        if self.controller == 'T':
            self._write(pack('B'*6,0x23,0x02,0x00,0x00,0x22,0x01))
        else:
            pass
    import os

    def read_file(self):
        filename = '\motor_settings.txt'
        filepath = os.path.dirname(__file__) + filename
        data = []
        lst = []
        with open(filepath,'r') as f:
            data =f.readlines()
        for i in range(len(data)):
            lst.append(data[i].split(','))
        for j in range(len(lst)):   
            lst[j] = [i.replace(' ','') for i in lst[j]]    
            lst[j] = [i.replace('\n','') for i in lst[j]]
        return lst        
        
    def identify(self):
        """
        This command is independent on the controller type
        page 28-29 of the communication protocol file
        send 6 bytes 05 00 00 00 11 01
        back 90 bytes
        0-5 bytes - header 06 00 54 00 d| s
        6-9 bytes - <--Serial Number-->
        10-17 bytes- <--Model Number-->
        18-19 bytes - <--Type-->
        20-23 bytes - <--Firmware Version-->
        24-83 bytes - <--For internal use only-->
        84-85 bytes - <--HW Version-->
        86-87 bytes - <--Mod State-->
        88-89 bytes - <--nchs--> "mnumber of channels"
        """
        command = pack('BBBBBB',0x05,0x00,0x00,0x00,0x11,0x01)
        result = self._inquiry(command)
        Header = self._unpack(result,0,5)
        SerialNumber = self._unpack(result,6,9) #unpack('L',result[6:10])
        ModelNumber = self._unpack(result,10,17)
        Type = self._unpack(result,18,19)
        FirmwareVersion = self._unpack(result,20,23)
        HWVersion = result[84:86]
        ForInternalUseOnly = result[24:84]
        ModState = self._unpack(result,86,87)
        nchs = self._unpack(result,88,89)
        print('The result of identify command: \n Header: %r \n Serial Number: %r \n Model Number: %r \n Type: %r \n Firmware Version: %r \n Mod State: %r \n nchs: %r \n For Internal Use Only: \n %r' % (Header, SerialNumber,ModelNumber,Type,FirmwareVersion, ModState,nchs,ForInternalUseOnly))
        
    def moveRel(self,Nsteps): #value in um
        pass
##        
##        if self.controller == 'K':
##            print('moving motor connected to the K cube')
##
##            
##        if self.controller == 'T':
##            print('moving motor connected to the T cube')
##            c_header = pack('BBBBBB',0x48,0x04,0x06,0x00,0xA2,0x01)
##            c_channel = pack('BB',0x01,0x00)
##            print('number of steps to move relative = %r' % Nsteps)
##            c_distance = pack('i',Nsteps)
##            command = c_header + c_channel + c_distance
##            print('command sent %r' % command)
##            response = self._inquiry(command)
##        return response

    def _moveAbs(self,NewPos):
        c_header = pack('BBBBBB',0x53,0x04,0x06,0x00,0x80,0x01) 
        c_channel = pack('BB',0x01,0x00)
        c_distance = pack('i',NewPos)
        command = c_header + c_channel + c_distance
        #print('command sent %r' % command)
        response = self._inquiry(command,20)
        res_pos = unpack('i',response[8:12])
        res_enc = unpack('i',response[12:16])
        res_status_bits = response[16:20]
        print('position %r , encoder %r, status bits %r' % (res_pos,res_enc,res_status_bits))

        
    def moveTo(self,NewPos): #value in um
        if NewPos > self.soft_limits[1] or NewPos < self.soft_limits[0]:
            flag = False
            response_str = 'out of limits'
        else:    
            if self.controller == 'K':
               print('moving motor %r connected to the %r cube' % (self.motor, self.controller))

            if self.controller == 'T':
     
                flag = False
                print('moving motor %r connected to the %r cube' % (self.motor, self.controller))
                print('number of steps to move relative = %r' % NewPos)
                CurPos = self.get_position()
                if (NewPos - CurPos)*sign(self.backlash) > 0: 
                    c_header = pack('BBBBBB',0x53,0x04,0x06,0x00,0x80,0x01)
                    c_channel = pack('BB',0x01,0x00)
                    c_distance = pack('i',NewPos)
                    command = c_header + c_channel + c_distance
                    #print('command sent %r' % command)
                    response = self._inquiry(command,20)

                elif (NewPos - CurPos)*sign(self.backlash) < 0:
                    c_header = pack('BBBBBB',0x53,0x04,0x06,0x00,0x80,0x01) 
                    c_channel = pack('BB',0x01,0x00)
                    c_distance = pack('i',NewPos-self.backlash)
                    command = c_header + c_channel + c_distance
                    #print('command sent %r' % command)
                    response = self._inquiry(command,20)
                    res_pos = unpack('i',response[8:12])
                    res_enc = unpack('i',response[12:16])
                    res_status_bits = response[16:20]
                    print('posigtion %r , encoder %r' % (res_pos,res_enc))
                    
                    c_distance = pack('i',NewPos)    
                    command = c_header + c_channel + c_distance
                    #print('command sent %r' % command)
                    response = self._inquiry(command,20)
                    
                else:
                    pass
            if self.get_position() == NewPos:
                flag = True
                response_str = 'move is complete'
        return flag, response_str
    
    
    def get_position(self):
        command = pack('BBBBBB',0x11,0x04,0x01,0x00,0x21,0x01)
        #print('Get position command sent %r' % command)
        response = self._inquiry(command,12)
        res_header = response[0:6]
        res_chan_ident = response[6:8]
        res_encoder_counts = response[8:12]
        return unpack('i',res_encoder_counts)[0]
    
    def set_position_1(self,value):
        c_header = pack('BBBBBB',0x09,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        Pos = self.get_position()
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        response = self._inquiry(command)
        return response
    
    def set_position_2(self,value):
        c_header = pack('BBBBBB',0x10,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        Pos = self.get_position()
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        response = self._inquiry(command)
        return response

    def set_position_3(self,value):
        c_header = pack('BBBBBB',0x11,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        Pos = self.get_position()
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        response = self._inquiry(command)
        return response
    
    def home(self):
        if self.motor == 'T':
            self._write(pack('BBBBBB',0x43,0x04,0x00,0x00,0x80,0x01))
            while self.ser.in_waiting == 0:
                sleep(0.1)
            result = self._read()    
        else:
            result = False
        return result



    
    def home_parameters_set(self,home_dir,limit_switch,home_velocity,offset_distance):
        """        MGMSG_MOT_SET_HOMEPARAMS 0x0440        """
        if self.motor == 'A':
            raise ValueError('This is AutoOptics motor and it does not have homing option!')
        else:
            c_header = pack('B'*6,0x40,0x04,0x0E,0x00,0xA2,0x01)
            c_channel = pack('BB',0x01,0x00) #<---this is always the same for TDC001 cubes.
            c_home_dir = pack('h',home_dir)
            c_limit_switch = pack('h',limit_switch)
            c_home_velocity = pack('l',home_velocity)
            c_offset_distance = pack('l',offset_distance)
            command = c_header + c_channel + c_home_dir + c_limit_switch + c_home_velocity + c_offset_distance
            response = self._inquiry(command)
            
    def home_parameters_get(self):
        """        MGMSG_MOT_GET_HOMEPARAMS 0x0442        """
        command = pack('B'*6,0x41,0x04,0x01,0x00,0x64,0x73)
        response = self._inquiry(command)
        res_header = response[0:7]
        res_chan_ident = response[6:8]
        res_home_dir = response[8:10]
        res_limit_switch = response[10:11]
        res_home_velocity = response[12:16]
        res_offset_distance = response[16:20]
        
        
        return res_home_dir,res_limit_switch,res_home_velocity,res_offset_distance


    def run_test1(self,N):
        from random import random
        lst = []
        to = []
        
        for i in range(N):
            start = time()
            goto = int(random()*6*512.*67.)
            dev6.moveAbs(goto)
            arrived = dev6.get_position()
            lst.append([time()-start,goto,arrived])
        print lst
            
            

    
dev = {}    
dev4 = motion_controller('COM9')


#dev.identify()

print('dev4.identify()')
print('dev6.identify()')
print('dev6.moveRel(1000)')
print('dev6._blink()')
print('dev6.get_position()')
print('dev6._moveAbs(0)')
print('dev6.run_test1(2)')
