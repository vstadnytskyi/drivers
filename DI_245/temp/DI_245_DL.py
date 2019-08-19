from numpy import concatenate,zeros,mean,std,uint16
#from CAServer import casput
from serial import Serial
from time import time, sleep,gmtime, strftime
from sys import stdout
import os.path
import matplotlib.pyplot as plt
from pdb import pm
from struct import unpack as struct_unpack
import logging
from logging import error,warn,info,debug
import circular_buffer_LL

__version__ = '1.0.5' #cleaned code, added comments
__date__ = "11-10-17"

class DI245_DL(object):
    def __init__(self,SN = 1):
        #this will create an instance
        self.SN = SN
        print('Initializing DL...')
        self.init_device(SN = self.SN)
        print('initializing buffer...')
        self.buffer = circular_buffer_LL.server(size = (4,4320000), var_type = 'int16')#4320000
        
    def init_device(self,SN = 1, scan_lst = ['0','1','2','3'], phys_ch_lst = ['0','1','2','3'], gain_lst = ['0.25','T-thrmc','0.25','T-thrmc']):#4320000
        self.SN = SN
        flag = True
        time_out = 0
        self._use_com_port('COM37')
        flag = False
        while flag:
            try:
                self._find_com_port()
                flag = False
            except:
                time_out += 1
                if time_out >10:
                    flag = False
		
        #create com port connection and flush it. It doesn't seem to be import to flush but why not.
        #self.ser = Serial(port, baudrate=115200, rtscts=True, timeout=0.1)
        self.ser.flushInput()
        self.ser.flushOutput()
        
        #Values
        self.cjc_value = -2.0 #this number needs to be tested with ice or another well calibrated thermocouple
        
        self.calib = [0.05,0,0.05,0,0] # [scale_up, offset_up, scale_down, offset_down, time] 50 mV per atm factory setting
        
        
        self.scan_lst = scan_lst
        self.phys_ch_lst = phys_ch_lst
        self.gain_lst = gain_lst
    
        self.channels_to_read = len(self.scan_lst)  
        #self.broadcast = 0            
        
        #dictionary with device parameters such as S\N, device name, ect
        self.dict_DI245 = {}
        self.dict_DI245['Device name'] = self._inquire('A1')[0][2:]
        self.dict_DI245['Firmware version'] = int(self._inquire('A2')[0][2:],16)/100.
        self.dict_DI245['Last Calibration date in hex'] = self._inquire('A7')[0][2:]
        self.dict_DI245['Serial Number'] = self._inquire('NZ')[0][2:]
        
        
        #Useful variables
        self.tau = 0.0001 #wait time after write (before) read. This seems to be not necessary. 
        
        
        for i in self.dict_DI245.keys():
            print i, self.dict_DI245[i]
        print 'Complete: Initialization of the DI-245 with S\N', self.dict_DI245['Serial Number']
        
        
        self._config_channels()

    
    def _use_com_port(self,port):
        self.ser = Serial(port, baudrate=115200, rtscts=True, timeout=0.1)
        self.stop_scan()
        
    def _find_com_port(self):
        #this function will scan com ports and find DI-245 devices by sending command A1 and receiving a word 2450 back
        import serial.tools.list_ports
        list = serial.tools.list_ports.comports()
        connected = []
        
        for element in list:
            print element.device
            try:
                self.ser = Serial(element.device, baudrate=115200, rtscts=True, timeout=0.1)
                self.stop_scan()
                try:
                    print 'DI device is avaiable:',self._inquire('A1')[0][2:]
                    if self._inquire('A1')[0][2:] == '2450':
                        print("the requested device is connected")
                    else:
                        print("DI-245 with requested serial number is not connceted")
                        self.ser.close()
                        print("closing com port")
                except:
                    self.ser._close_port()
            except:
                pass

                    
    def _read(self):
        sleep(self.tau)
        lines =  self.ser.readlines() # Friedrich doesn't like command readline, since "The method readline() reads one entire line from the file.
        #However, my tests have showed if you know what you expect to get it always works. Just make sure you have "
        stdout.flush()
        return lines[0] #I am not sure why do I have to specify index 0 in this list
    
    def _write(self,command):
        self.ser.flushOutput()
        self.ser.write(command)
        

    def _inquire(self,command):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(command)
        return self.ser.readlines() 
    
    def _close_port(self):
        self.ser.close()

    #Scanning\data acquisition section
    #an example: chn(0x20)member(0x20)value(0x0D)
    #2-byte value needs to be converted from binary to int. The binary 2 byte start counting from right.
    #The values in the function definition are default values in case user does not specify them.
    def _config_channels(self):
        #self.scan_lst = ['0','1','2','3']
        #self.phys_ch_lst = ['0','1','2','3']
        #self.gain_lst = ['2.5','2.5','2.5','2.5']
        #This method needs to be rewritten to take a list instead of a set of parameters. This will help with scalability. 
        
        _config_dict_gain = {}
        _config_dict_gain['0.010'] = '00101'
        _config_dict_gain['0.025'] = '00100'
        _config_dict_gain['0.05'] = '00011'
        _config_dict_gain['0.1'] = '00010'
        _config_dict_gain['0.25'] = '00001'
        _config_dict_gain['0.5'] = '00000'
        _config_dict_gain['1'] = '01101'
        _config_dict_gain['2.5'] = '01100'
        _config_dict_gain['5'] = '01011'
        _config_dict_gain['10'] = '01010'
        _config_dict_gain['25'] = '01001'
        _config_dict_gain['50'] = '01000'
        _config_dict_gain['B-thrmc'] = '10000'
        _config_dict_gain['E-thrmc'] = '10001'
        _config_dict_gain['J-thrmc'] = '10010'
        _config_dict_gain['K-thrmc'] = '10011'
        _config_dict_gain['N-thrmc'] = '10100'
        _config_dict_gain['R-thrmc'] = '10101'
        _config_dict_gain['S-thrmc'] = '10110'
        _config_dict_gain['T-thrmc'] = '10111'
        
        for i in range(len(self.scan_lst)):
            config_byte = str(int('000'+_config_dict_gain[self.gain_lst[i]]+'0000' + bin(int(self.phys_ch_lst[i]))[2:].zfill(4),2))
            ch_config_command = 'chn '+self.scan_lst[i]+' '+config_byte+' \x0D'
        
            self.ser.flushInput()
            self.ser.flushOutput()
            result1 = self._inquire(ch_config_command)
        
        xrate_config_command = 'xrate 4099 2000 \x0D'
        #xrate_config_command = 'xrate 62 127 \x0D' #good slow 
        #xrate_config_command = 'xrate 1871 10 \x0D'
        #xrate_config_command = 'xrate 2051 2000\x0D'
        result2 = self._inquire(xrate_config_command) #config xrate for the data acquisition
        
        print 'Complete: Channel(s) and xrate configuration' 
        return result1, result2
        
    #this method sends a proper command to start the scan.    
    def start_scan(self):
        read_byte_temp = ""        
        while read_byte_temp != 'S1':
            self._write('S1')
            read_byte_temp = self.ser.read(2) #read 2-byte echo respons
        print 'The configured measurement(s) has(have) started'
    
    #This method reads one
    def read_number(self):
        value_array = zeros((self.channels_to_read))
        for j in range(self.channels_to_read):
            #value_array[2*j] = time.time()
            tempt_t = time()
            read_byte = self.ser.read(2)
            read_byte = bin(struct_unpack("H", read_byte)[0])[2:].zfill(16)
            read_byte_lst = list(read_byte)
            sync_byte = read_byte_lst[15] #this is the byte 0 that is issued in DI-245 for sync. 0 stand for the beginning of channel(s) data stream. Hence, every set of readouts  starts with 0. 
            del(read_byte_lst[15]) #This is so called sync bit, it is 0 in the beginning of a new sequence of data
            del(read_byte_lst[7])  
            read_byte = ""
            for i in read_byte_lst:
                read_byte += str(i)
            int_val = int(read_byte,2)
            value_array[j] = int_val
        return value_array
        
    def _waiting(self):
        logging.debug('In ' + str(self.ser.in_waiting) + '  Out '+ str(self.ser.out_waiting)) #these commands tell how many bytes are in RS-232 buffer in and out
        
    def stop_scan(self):
        self._inquire('S0')
        
    def full_stop(self):
        self.stop_scan()
        self._close_port()
    
   
    
    def _int_to_units(self, array_in, channel):
        if channel == 'all':
            array_out = zeros(4)
            array_out[0]  = (((array_in[0]-8192.)/8192.)*float(self.gain_lst[0]))/self.calib[0]
            array_out[1]  = ((array_in[1]-8192.)*0.036621+100. - self.calib[1])
            array_out[2]  = (((array_in[2]-8192.)/8192.)*float(self.gain_lst[2]))/self.calib[2]
            array_out[3]  = ((array_in[3]-8192.)*0.036621+100. - self.calib[3])
        elif channel == 0:
            array_out = (((array_in-8192.)/8192.)*float(self.gain_lst[channel]))/self.calib[0]
        elif channel == 1:	
            array_out  = ((array_in-8192.)*0.036621+100. + self.cjc_value)
        elif channel == 2:
            array_out = (((array_in-8192.)/8192.)*float(self.gain_lst[channel]))/self.calib[2]
        elif channel == 3:	
            array_out  = ((array_in-8192.)*0.036621+100. + self.cjc_value)
        elif channel == 'rms_ch0':
            array_out = ((float(self.gain_lst[0]))/self.calib[0])/8192.
        elif channel == 'rms_ch1':
            array_out = (float(self.gain_lst[1]))*0.036621
        elif channel == 'rms_ch2':
            array_out = ((float(self.gain_lst[2]))/self.calib[2])/8192.
        elif channel == 'rms_ch3':
            array_out = (float(self.gain_lst[3]))*0.036621	
        return array_out
    
    def set_calib(self):
        print '_set_calibration'
        #self.calib = [0.05,0,0.05,0,0] # [scale_up, offset_up, scale_down, offset_down, time] 50 mV per atm factory setting
        #while self.RingBufferPointer < 50*1:
        #    time.sleep(1)
        a = mean(((self.buffer.get_last_N(N = 300)[0]-8192.)/8192.)*float(self.gain_lst[0]))
        b = mean(self.buffer.get_last_N(N = 300)[1]-8192.)*0.036621+100.-self.calib[1]
        c = mean(((self.buffer.get_last_N(N = 300)[2]-8192.)/8192.)*float(self.gain_lst[2]))
        d = mean(self.buffer.get_last_N(N = 300)[3]-8192.)*0.036621+100.-self.calib[3]
        self.calib = [a,b ,c ,d , time()]
        print self.calib
        print "-------"
        
    def save_to_a_file(self):
        debug('save to a file pressed %r' % time())
        pass
 
    def broadcast(self, method = "on demand"):

        if method == "on demand":
            debug('Broadcasting on demand')
            casput("NIH:DI245."+str(self.dict_DI245['Serial Number'])+".CH1.pressure",self._int_to_units(int(mean(self.buffer.get_last_N(N = 50)[0])),0))
            casput("NIH:DI245."+str(self.dict_DI245['Serial Number'])+".CH2.temperature",self._int_to_units(int(mean(self.buffer.get_last_N(N = 50)[1])),1))
            casput("NIH:DI245."+str(self.dict_DI245['Serial Number'])+".CH3.pressure",self._int_to_units(int(mean(self.buffer.get_last_N(N = 50)[2])),2))
            casput("NIH:DI245."+str(self.dict_DI245['Serial Number'])+".CH4.temperature",self._int_to_units(int(mean(self.buffer.get_last_N(N = 50)[3])),3))
            print("NIH:DI245."+str(self.dict_DI245['Serial Number'])+".CH4.temperature",self._int_to_units(int(mean(self.buffer.get_last_N(N = 50)[3])),3))
            
        else:
            pass#debug("unknown method(%r) requested" % method)

if __name__ == "__main__":
    logging.basicConfig(filename='di_245_DL.log', level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    dev = DI245_DL()
    print("----------------------")
    print("DI-245 Device Level library")
    print("----------------------")
    print("-----Basic functions-----")
    print("RING BUFFER commands need to be added")
    print("dev.init_device() #-> will use preconfigured sequence")
    print("dev._use_com_port(port)")
    print("dev._find_com_port()")                   
    print("dev._read()")
    print("dev._write(self,command)")
    print("dev._inquire(command)")
    print("dev._waiting()")
    print("dev._close_port()")
    print("-----Advance functions-----")
    print("dev.config_channels()")   
    print("dev.start_scan()")
    print("dev.read_number()")       
    print("dev.stop_scan()")
    print("dev.full_stop()")
    print("dev._int_to_units()")
    print("dev.set_calib()")
    print("dev.save_to_a_file()")
    print("dev.broadcast()")
