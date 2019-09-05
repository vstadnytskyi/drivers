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
import usb
from struct import pack, unpack
from pdb import pm
from logging import debug,info,warning, error
import traceback


class ThorLabs_T_Motor(object):
    def __init__(self):
        self.motor = 'T'
        self.controller = 'T'

    def init(self,serial_number = '83825160'):
        self.serial_number = serial_number
        self.dev = self.find(self.serial_number)
        self.configuration()
        self.get_usb_information()

    def find_all(self):
        """returns dev object for a given serial_number"""
        import usb
        dev = None
        devices = list(usb.core.find(idVendor=0x0403, idProduct=0xFAF0, find_all = True))
        return devices

    def find(self,serial_number):
        """returns dev object for a given serial_number"""
        import usb
        dev = None
        devices = list(usb.core.find(idVendor=0x0403, idProduct=0xFAF0, find_all = True))
        for dev in devices:
            if dev.serial_number == serial_number:
                break
            else:
                dev = None
        return dev

    def configuration(self):
        reattach = False
        if self.dev.is_kernel_driver_active(0):
            reattach = True
            self.dev.detach_kernel_driver(0)
        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()
        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]
        self.epo = usb.util.find_descriptor(
                                      intf,
                                      # match the first OUT endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_OUT)

        self.epi = usb.util.find_descriptor(
                                      intf,
                                      # match the first IN endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_IN)

        assert self.epo is not None
        assert self.epi is not None
        self.epi.wMaxPacketSize = 72000
        self.epo.wMaxPacketSize = 72000
        self.epi.bmAttributes = 1
        self.epi.bInterval = 100
        self.usb_buff = int(self.epi.wMaxPacketSize/100)

    def get_usb_information(self):
        if self.dev != None:
            self.dev_dict = {}
            self.epi_dict = {}
            self.dev_dict['DEV:address'] = self.dev.address
            self.dev_dict['DEV:bDeviceClass'] = self.dev.bDeviceClass
            self.dev_dict['DEV:bDescriptorType'] = self.dev.bDescriptorType
            self.dev_dict['DEV:bDeviceProtocol'] = self.dev.bDeviceProtocol
            self.dev_dict['DEV:bLength'] = self.dev.bLength
            self.dev_dict['DEV:bMaxPacketSize0'] = self.dev.bMaxPacketSize0
            self.dev_dict['DEV:bNumConfigurations'] = self.dev.bNumConfigurations
            self.dev_dict['DEV:manufacturer'] = self.dev.manufacturer
            self.dev_dict['DEV:serial_number'] = self.dev.serial_number
            self.dev_dict['DEV:speed'] = self.dev.speed
            self.dev_dict['DEV:product'] = self.dev.product

            #endpoint IN description
            self.epi_dict['EPI:bmAttributes'] = self.epi.bmAttributes
            self.epi_dict['EPI:wMaxPacketSize'] = self.epi.wMaxPacketSize
            self.epi_dict['EPI:bSynchAddress'] = self.epi.bSynchAddress
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval
            self.epi_dict['EPI:bEndpointAddress'] = self.epi.bEndpointAddress
            self.epi_dict['EPI:bDescriptorType'] = self.epi.bDescriptorType
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval

    """Basic serial communication functions"""

    def read(self,N = 0):
        if N == 0:
            usb_buff = int(self.usb_buff)
        else:
            usb_buff = int(N)
        from time import sleep
        #tested dec 17, 2017
        string = b""
        timeout = 1000
        try:
            data = self.dev.read(self.epi,usb_buff,timeout)
        except:
            error(traceback.format_exc())
            data = ''

        if len(data) != 0:
            for i in data:
                string += bytes([i])
        return string

    def readall(self):
        return self.read(0) #0 will read all

    def write(self,command):
        try:
            self.dev.write(self.epo,command)
        except:
            error(traceback.format_exc())

    def query(self,command, N = 0):
        self.write(command)
        if N == 0:
            N = self.usb_buff
        res = self.read(N)
        print('result of query = %r' %res)
        return res

    def setup(self,dev):
        """initialization function"""
        #this will turn on message to be send upon completion of the move.
        self.ser.write(pack('BBBBBB',0x6C,0x04,0x00,0x00,0x80,0x01))
        #suspend end of motion message
        #self.ser.write(pack('BBBBBB',0x6B,0x04,0x00,0x00,0x21,0x01))
        """MGMSG_HW_NO_FLASH_PROGRAMMING"""
        #self.ser.write()



    def blink(self):
        self.write(command = pack('B'*6,0x23,0x02,0x00,0x00,0x50,0x01))



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
        result = self.query(command,90)
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
        print('The result of identify command: \n Header: %r \n Serial Number: %r \n Model Number: %r \n Type: %r \n Firmware Version: %r \n Mod State: %r \n nchs: %r \n For Internal Use Only: \n %r' % (Header, SerialNumber,ModelNumber,Type,FirmwareVersion, ModState,nchs,ForInternalUseOnly))



    def move_abs(self,new_pos):
        flag = False
        comment = None
        if self.controller == 'T' and self.motor == 'T':
            c_header = pack('BBBBBB',0x53,0x04,0x06,0x00,0x80,0x01)
            c_channel = pack('BB',0x01,0x00)
            c_distance = pack('i',new_pos)
            command = c_header + c_channel + c_distance
            #print('command sent %r' % command)
            response = self.query(command,20)
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
        response = self.query(command,12)
        res_header = response[0:6]
        res_chan_ident = response[6:8]
        res_encoder_counts = response[8:12]
        return unpack('i',res_encoder_counts)[0]

    def set_position(self,value):
        c_header = pack('BBBBBB',0x09,0x04,0x06,0x00,0xA2,0x01)
        c_channel = pack('BB',0x01,0x00)
        c_distance = pack('i',value)
        command = c_header + c_channel + c_distance
        self.write(command)


    def home(self):
        '''MGMSG_MOT_MOVE_HOME'''
        flag = False
        if self.motor == 'T':
            res = self.query(pack('B'*6,0x43,0x04,0x00,0x00,0xA2,0x01),6)
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
            print(i)
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
            response = self.query(command)

    def home_parameters_get(self):
        """        MGMSG_MOT_GET_HOMEPARAMS 0x0442        """
        from struct import unpack
        command = pack('B'*6,0x41,0x04,0x01,0x00,0x64,0x73)
        response = self.query(command,20)
        print(response)
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
    print('motor = ThorLabs_T_Motor(); cube.motor = "T"; cube.controller = "T"')
    print("motor.init(serial_number = '8382516')")
    print('motor.moveAbs(0)')
    print('motor.get_position()')
    print('motor.set_position()')
    print('motor.home()')
    print('motor.blink()')
    motor = ThorLabs_T_Motor();
    motor1 = ThorLabs_T_Motor();
    motor1.init(serial_number = '83825160')
    motor.init(serial_number = '27254090')
    motor.blink()
    motor.read(100)
