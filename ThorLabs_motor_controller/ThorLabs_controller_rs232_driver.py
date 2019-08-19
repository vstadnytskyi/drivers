#!/bin/env python
"""
ThorLabs TDC001 and KDC001 cubes Low Level code.
This code specifies communication protocola for T snd K cubes.

Valentyn Stadnytskyi
valentyn.stadnytskyi@nih.gov

The communication protocols:
https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf issue 20
"""
from time import sleep, time
from numpy import zeros, ones, mean, std, sign
from serial import Serial
from struct import pack, unpack
from pdb import pm
import logging
from logging import debug, info, warn, error


class Motor(object):
    def __init__(self):
        self.baudrate = 115200
        self.controller = 'T'
        self.motor = 'T'
        self.last_communiction = {}

    def list_all(self):
        """
        lists and returns all com ports with the manufacturer field equal to 'ThorLabs'
        """
        import serial.tools.list_ports
        lst = serial.tools.list_ports.comports()
        available_ports = []
        for item in lst:
            debug(item.manufacturer)
            if item.manufacturer == 'Thorlabs':
                available_ports.append(item)
        return available_ports

    def get_port(self, serial_number = None):
        """
        returns the name of the serial port for the ThorLabs motor controller with specified serial_number
        """
        def is_port_open(port):
            from serial import Serial
            import platform
            if platform.system() == 'Linux':
                prefix = '/dev/'
            else:
                prefix = ''
            ser = Serial(prefix+port, baudrate=115200, bytesize = 8, parity='N', stopbits=1, timeout=1)
            ser.isOpen()
        import platform
        if platform.system() == 'Linux':
            prefix = '/dev/'
        else:
            prefix = ''
        lst = self.list_all()
        port_name = ''
        if serial_number != None:
            for item in lst:
                if item.serial_number == str(serial_number):
                    port_name = prefix+item.name
        return port_name

    def get_serial_object(self,port_name):
        "connects to a given port name /dev/ttyUSB1 in case of linux"
        from serial import Serial
        ser = Serial(port_name, baudrate=self.baudrate, bytesize = 8, parity='N', stopbits=1, timeout=1)
        return ser

    def init(self, serial_number = ''):
        if serial_number != "":
            port_name = self.get_port(serial_number = serial_number)
            ser = self.get_serial_object(port_name = port_name)
            if ser is not None:
                self.ser = ser
            else:
                print('No serial device with serial number {}'.format(serial_number))
        else:
            print('Serial Number has to be specified')

    def initialization(self):
        """initialization function"""
        #this will turn on message to be send upon completion of the move.

        #I ran this command and it turned off reply to identify
        #self.ser.write(pack('BBBBBB',0x6C,0x04,0x00,0x00,0x80,0x01))

        #suspend end of motion message
        #self.ser.write(pack('BBBBBB',0x6B,0x04,0x00,0x00,0x21,0x01))
        """MGMSG_HW_NO_FLASH_PROGRAMMING"""
        #self.ser.write()
        pass

    def read(self, N = 0):
        if N ==0:
            result = None
        else:
            result = self.ser.read(N)
        return result

    def write(self,command):
        self.flush()
        self.ser.write(command)

    def inquiry(self,command, length = None):
        """write read command"""
        self.write(command)
        result = self.ser.readline()
        return result
    self.query = self.inquiry

    def inquiry_old(self,command, length = None):
        """write read command"""
        self.write(command + '\r')
        if length == None:
            result = None
        else:
            while self.ser.in_waiting < length:
                sleep(0.1)
            result = self.read(N = length)
        return result

    def close(self):
        self.ser.close()
        del self.ser

    def waiting(self):
        return [self.ser.in_waiting,self.ser.out_waiting]

    def flush(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def blink(self):
        if self.controller == 'T':
            self.write(pack('B'*6,0x23,0x02,0x00,0x00,0x50,0x01))
            flag = True
        else:
            flag = False


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
        command = pack('BBBBBB',0x05,0x00,0x00,0x00,0x50,0x01)
        result = self.inquiry(command,90)
        self.full_result = result
        Header = result[0:6]
        SerialNumber = unpack('i',result[6:10]) #unpack('L',result[6:10])
        ModelNumber = result[10:18]
        Type = unpack('h',result[18:20])
        FirmwareVersion = self.my_unpack(result,20,23)
        HWVersion = result[84:86]
        ForInternalUseOnly = result[24:84]
        ModState = self.my_unpack(result,86,87)
        nchs = self.my_unpack(result,88,89)
        msg = ""
        debug('The result of identify command: \n Header: %r \n Serial Number: %r \n Model Number: %r \n Type: %r \n Firmware Version: %r \n Mod State: %r \n nchs: %r \n For Internal Use Only: \n %r' % (Header, SerialNumber,ModelNumber,Type,FirmwareVersion, ModState,nchs,ForInternalUseOnly))
        res_dic = {}
        res_dic['Header'] = Header
        res_dic['SerialNumber'] = SerialNumber
        res_dic['ModelNumber'] = ModelNumber
        res_dic['Type'] = Type
        res_dic['FirmwareVersion'] = FirmwareVersion
        res_dic['HWVersion'] = HWVersion
        res_dic['ForInternalUseOnly'] = ForInternalUseOnly
        res_dic['ModState'] = ModState
        res_dic['nchs'] = nchs
        return res_dic


    def move_abs(self,new_pos):
        flag = False
        comment = None
        if self.controller == 'T' and self.motor == 'T':
            c_header = pack('BBBBBB',0x53,0x04,0x06,0x00,0x80,0x01)
            c_channel = pack('BB',0x01,0x00)
            c_distance = pack('i',new_pos)
            command = c_header + c_channel + c_distance
            #print('command sent %r' % command)
            response = self.inquiry(command,20)
            res_pos = unpack('i',response[8:12])
            res_enc = unpack('i',response[12:16])
            res_status_bits = response[16:20]
            #talk to Fridriech about this issue with bits
            #print('position %r , encoder %r, status bits %r' % (res_pos,res_enc,res_status_bits))
            #if res_status_bits == pack('BBBB',0x00,0x04,0x00,0x90):
            #    flag = True
            #3if res_status_bits == pack('BBBB',0x01,0x04,0x00,0x90):
            #    comment = 'Hard Limit Low'
            #if res_status_bits == pack('BBBB',0x6F,0x76,0x45,0x72):
            #    comment = 'Over'
            flag = True
        return flag, comment

    def get_position(self):
        """FIXIT: add description"""
        command = pack('BBBBBB',0x11,0x04,0x01,0x00,0x21,0x01)
        #print('Get position command sent %r' % command)
        response = self.inquiry(command,12)
        res_header = response[0:6]
        res_chan_ident = response[6:8]
        res_encoder_counts = response[8:12]
        self.last_communiction['command'] = command
        self.last_communiction['response'] = response
        return unpack('i',res_encoder_counts)[0]

    def set_position(self,value):
        """
        """
        c_header = pack('BBBBBB',0x09,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        self.write(command)


    def home(self):
        '''MGMSG_MOT_MOVE_HOME'''
        flag = False
        if self.motor == 'T':
            self.write(pack('B'*6,0x43,0x04,0x00,0x00,0xA2,0x01))
            while self.ser.in_waiting == 0:
                sleep(0.1)
            res = self.read(6)
        if res == pack('BBBBBB',0x44,0x04,0x01,0x00,0x01,0x80):
            print('%r' % res)
            flag = True
        else:
            print(res)
        return flag, res #returns True of home was succesfully executed.

    def my_unpack(self,var,f,t):
        return unpack('B'*len(var[f:t+1]),var[f:t+1])

    def hex_to_chr(self, var):
        for i in var:
            print i
            string =+ chr(var)
        return string
    """Potentially useful commands. Haven;t been used or extensively tested"""



    def set_position_2(self,value):
        c_header = pack('BBBBBB',0x10,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        Pos = self.get_position()
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        response = self.inquiry(command)
        return response






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
            response = self.inquiry(command)

    def home_parameters_get(self):
        """        MGMSG_MOT_GET_HOMEPARAMS 0x0442        """
        from struct import unpack
        command = pack('B'*6,0x41,0x04,0x01,0x00,0x64,0x73)
        response = self.inquiry(command,20)
        res = {}
        res['header'] = response[0:7]
        res['chan_ident'] = unpack('h',response[6:8])
        res['home_dir']= unpack('h',response[8:10])
        res['limit_switch'] = unpack('b',response[10:11])
        res['home_velocity'] = unpack('i',response[12:16])
        res['offset_distance'] = unpack('i',response[16:20])


        return res


    def run_test1(self,N):
        from random import random
        from time import sleep, time
        lst = []
        to = []

        for i in range(N):
            start = time()
            prev = self.get_position()
            goto = int(random()*25*512.*67.)
            self.move_abs(goto)
            while abs(goto - self.get_position()) > 3:
                sleep(0.3)
            arrived = self.get_position()
            print [time()-start,round(goto/(512.*67.),2),round(arrived/(512.*67.),2),round((goto-prev)/(512.*67.*(time()-start)),2)]
            sleep(5)





if __name__ == "__main__":

    print('This is a Low Level python script providing Device Level with basic communication commands')
    print('cube = Cube("COM6"); cube.motor = "T"; cube.controller = "T"')
    print('cube.initialization()')
    print('cube.moveAbs(0)')
    print('cube.get_position()')
    print('cube.set_position()')
    print('cube.home()')
    print('cube.blink()')
