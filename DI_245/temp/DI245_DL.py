"""
Temlpate for Device Level code
author: Valentyn Stadnytskyi
created: March 19 2019
last updated: March 19 2019

designed with Python 3 in mind.


"""
__version__ = '1.0.0'

import traceback
import psutil, os, sys
import platform #https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
p = psutil.Process(os.getpid()) #source: https://psutil.readthedocs.io/en/release-2.2.1/
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITY_CLASS
if platform.system() == 'Windows':
    p.nice(psutil.REALTIME_PRIORITY_CLASS)
elif platform.system() == 'Linux': #linux FIXIT
    p.nice(-20) # nice runs from -20 to +12, where -20 the most not nice code(highest priority)

from numpy import nan, mean, std, nanstd, asfarray, asarray, hstack, \
     array, concatenate, delete, round, vstack, hstack, zeros, \
     transpose, split, unique, nonzero, take, savetxt, min, max
from time import time, sleep
import sys

import struct
from pdb import pm
from time import gmtime, strftime, time
from struct import pack, unpack
from timeit import Timer, timeit
from threading import Thread, Event, Timer, Condition
from datetime import datetime

if sys.version_info[0] ==3:
    from persistent_property.persistent_property3 import persistent_property
    from _thread import start_new_thread
    from time import process_time as clock
    from logging import debug,info,warn,error
    from logging import warning as warn
else:
    from persistent_property.persistent_property import persistent_property
    from thread import start_new_thread
    from time import clock
    from logging import debug,info,warn,error



from XLI.precision_sleep import precision_sleep #home-made module for accurate sleep
from XLI.circular_buffer_LL import CBQueue, CBServer, CBClient #home-made module with circular buffers and queues
from XLI.hierarchy_instrumentation import XLevelTemplate, IndicatorsTemplate, ControlsTemplate #Classes for different objects


##################################################################################################################
##################################################################################################################
######  Indicators  ######
##################################################################################################################
##################################################################################################################
###### Description ######
##"""
##The Indicators Class inherits properties from IndicatorsTemplate in XLI package
##"""
##"""
##There are handfull of important functions that each Indicators class has has:
##- get           # returns a dictionary of all avaiable controls and theit current values     
##
##"""
##
##"""
##The typical structure of indicators variables.
##get funtion, that will be executed if the server-IO will get a command to retrieve indicator variable.
##Usually, these indicators have dublicated in template_dl module or some other module for easier management.
##
##Example:
##def get_s_frequency(self):
##    return icarus_dl.pr_rate
##s_frequency = property(get_s_frequency)
##"""
##################################################################################################################


class Indicators(IndicatorsTemplate):

    ###Data Acquisision module indicators

    def get(self, value = None):
        response = {}
        response[b'running'] = self.running
        response[b'device_name'] = self.device_name
        response[b'serial_number'] = self.serial_number
        response[b'firmware_version'] = self.firmware_version
        response[b'freq'] = self.freq


        response[b'pressure_upstream'] = self.pressure_upstream
        response[b'pressure_downstream'] = self.pressure_downstream
        response[b'pressure_barometric'] = self.pressure_barometric
        response[b'temperature'] = self.temperature

        response[b'start_time'] = self.start_time
        response[b'channels_description'] = self.channels_description
        
        
        response = self.get_cb_indicators(response)
        ###indicators to add
        return response

    def get_cb_indicators(self,dic):
        if len(device_level.circular_buffers) != 0:
            for key in list(device_level.circular_buffers.keys()):
                cb_type = device_level.circular_buffers[key].type
                value = device_level.circular_buffers[key].get_last_N(1)
                pointer = device_level.circular_buffers[key].pointer
                g_pointer = device_level.circular_buffers[key].g_pointer
                if sys.version[0] == '3':
                    dic[b'CB '+bytes(cb_type,encoding='utf8')+bytes(' ',encoding='utf8')+key] = {b'value':value,b'pointer':pointer,b'g_pointer':g_pointer}
                elif sys.version[0] == '2':
                    dic[b'CB '+bytes(cb_type)+bytes(' ')+key] = {b'value':value,b'pointer':pointer,b'g_pointer':g_pointer}
        
        return dic

    def get_running(self):
        """

        """
        try:
            response = getattr(device_level,'running')
        except:
            response = None #device.controls.running
            warn(traceback.format_exc())
        return response
    def set_running(self,value):
        setattr(device_level,'running',value)
    running = property(get_running,set_running)


    def get_device_name(self):
        try:
            response = device_level.device_name
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    device_name = property(get_device_name)

    def get_serial_number(self):
        try:
            response = device_level.serial_number
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    serial_number = property(get_serial_number)

    def get_firmware_version(self):
        try:
            response = device_level.firmware_version
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    firmware_version = property(get_firmware_version)

    def get_freq(self):
        try:
            response = device_level.freq
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    freq = property(get_freq)

    def get_pressure_upstream(self):
        from numpy import mean
        try:
            response = device_level.pressure_upstream
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    pressure_upstream = property(get_pressure_upstream)

    def get_pressure_downstream(self):
        from numpy import mean
        try:
            response = device_level.pressure_downstream
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    pressure_downstream = property(get_pressure_downstream)
    
    def get_pressure_barometric(self):
        from numpy import mean
        try:
            response = device_level.pressure_barometric
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    pressure_barometric = property(get_pressure_barometric)
    
    def get_temperature(self):
        from numpy import mean
        try:
            response = device_level.temperature
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    temperature = property(get_temperature)

    def get_start_time(self):
        try:
            response = device_level.start_time
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    start_time = property(get_start_time)

    def get_channels_description(self):
        try:
            response = device_level.channels_description
        except:
            response = ['None' ,'None','None','None']
            warn(traceback.format_exc())
        return response
    channels_description = property(get_channels_description)





##################################################################################################################
##################################################################################################################
######  Controls  ######
##################################################################################################################
##################################################################################################################
###### Description ######
    """
    The Controls Class inherits properties from ControlsTemplate in XLI package
    """
    """
    There are handfull of importamt functions that each Controls class has has:
    - get           # returns a dictionary of all avaiable controls and theit current values
    - set           # sets one or several controls to specified values.      

    """

    """
    The typical structure of control variables.
    first, set function, that will be executed if the server-IO will get a command to change control variable.
    second, get funtion, that will be executed if the server-IO will get a command to retrieve control variable.
    Usually, this controls have dublicated in template_dl module for easier 

    Example:
    def set_value(self, value = 1):
        template_dl.value = value
    def get_value(self):
        try:
            response = template_dl.value
        except:
            response = 0
        return response
    value = property(get_value,set_value)
    """
##################################################################################################################


class Controls(ControlsTemplate):

    def get(self):
        """defines a list of avaiable indicators.
        Input: None
        Output: dictionary with all avaialable indicators
        
        Note: indicators needs to be manually added to be available.
        """
        response = {}
        response[b'update_period'] = self.update_period
        return response

    def set_update_period(self, value = 1):
        device_level.update_period = value
    def get_update_period(self):
        try:
            response = device_level.update_period
        except:
            response = 0
        return response
    update_period = property(get_update_period,set_update_period)

##################################################################################################################
##################################################################################################################
######  Template Device Level ######
##################################################################################################################
##################################################################################################################
###### Description ######
    """
    There are handfull of functions that each DL has:
    - init                  # initializes DL
    - abort                 # aborts current scheduled tasks execuation
    - close                 # closes the DL
    - snapshot              # provides a quick update of the DL as snapshot 
    - notify_subscribers    # notifies all subscribers about updates on demand
    - controls              # returns all controls
    - indicators            # returns all indicators
    - schedule              # schedules execution of tasks
    - get_circular_buffer   # returns part of a requested circular buffer
    """

    """
    There are handfull of important instances or dictionaries
    - inds                  # indicators instance (see Indicators Class)
    - ctrls                 # controls instance (see Controls Class)
    - circular_buffers      # dictionary of all circular buffers, or queues.
    """
##################################################################################################################

class DI245_DL(XLevelTemplate):
    CA_prefix = persistent_property('CA_prefix', 'NIH:')
    scan_lst = persistent_property('scan_lst', ['0','1','2','3'])
    phys_ch_lst = persistent_property('phys_ch_lst', ['0','1','2','3'])
    gain_lst = persistent_property('gain_lst', ['5','5','5','T-thrmc'])
    calib = persistent_property('calib', [0,0,0,0,0])
    time_out = persistent_property('time_out', 2)
    cjc_value = persistent_property('cjc_value', '')
    serial_number = persistent_property('serial_number', '')
    circular_buffer_size = persistent_property('circular_buffer_size', (4,4320000))
    freq = persistent_property('freq', '')
    update_period = persistent_property('update_period',10)
    
    inds = Indicators()
    ctrls = Controls()
    circular_buffers = {}

    def setup_first_time(self):
        #self.SN = '57D81C13'
        self.scan_lst = ['0','1','2','3']
        self.phys_ch_lst = ['0','1','2','3']
        self.gain_lst = ['5','5','5','T-thrmc']
        self.circular_buffers_size = {b'main':4320000,b'history':8640*7}
        self.time_out = 0.1
        self.cjc_value = -2.0 #this number needs to be tested with ice or another well calibrated thermocouple
        self.calib = [0.025,0,0.025,0,0] # [scale_up, offset_up, scale_down, offset_down, time] 50 mV per atm factory setting
        self.freq = 50
        self.firmware_vesrion = 0
        self.update_period = 10
    def init(self, msg_in = None, client = None):

        """
        initialize the DL program
        """
        self.name = 'DI245_DL'
        self.circular_buffers[b'main'] = CBServer(size = (4,4320000), var_type = 'int16')
        self.circular_buffers[b'history'] = CBServer(size = (5,8640*7), var_type = 'float64')

        self.channels_description = ['pressure upstream','pressure downstream','pressure barometric','temperature']

        self.description = ''
        flag = False
        message = None
        err = ''
        flag, message, err = driver.init()
        if flag:
            driver.config_channels(scan_lst = self.scan_lst,
                                       phys_ch_lst = self.phys_ch_lst,
                                       gain_lst = self.gain_lst,
                                       rate = 0)
            driver.start_scan()
            self.start_time = None
            self.start()

        self.device_name = driver.dict_DI245[b'Device name']
        self.serial_number = driver.dict_DI245[b'Serial Number']
        self.firmware_version = driver.dict_DI245[b'Firmware version']
        self.freq = driver.dict_DI245[b'freq']

        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def abort(self, msg_in = None, client = None):

        """
        abort current execution
        """
        flag = False
        buff = None
        err = ''
        message = ''

        
        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def close(self, msg_in = None, client = None):
        """
        close the DL program
        """
        self.stop()
        sleep(0.5)
        driver.stop_scan()
        sleep(0.5)
        driver.close_port()
        flag = True
        buff = None
        message = ''
        err = ''

        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def snapshot(self, msg_in = None, client = None):
        """returns a snapshot"""
        flag = False
        message = {}
        message[b'description'] = self.description
        message[b'indicators'] = self.inds.get()
        message[b'controls'] = self.ctrls.get()
        buff = None
        err = ''
        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def notify_subscribers(self, msg_in = None, client = None):
        flag = False
        buff = {}
        buff = None
        err = ''

        
        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    #def controls(self, msg_in = None, client = None):
    #build in controls function. See the class file for details

    #def indicators(self, msg_in = None, client = None):
    #build in indicators function. See the class file for details

    #def schedule_task_queue(self, msg_in = None, client = None):
    #build in schedule task queue function. See the class file for details  

    #def circular_buffer(self, msg_in = None, client = None):
    #build in get circular buffer function. See the class file for details    

##################################################################################################################
##################################################################################################################
######  Threading Section  ######
##################################################################################################################
##################################################################################################################
######
##################################################################################################################

    def stop(self):
        """"""
        self.running = False

    def run_once(self):
        """
        """
        N_of_points = 4
        
        data = driver.read_number(N_of_channels = 4, N_of_points = int(N_of_points))
        if self.start_time is None:
            self.start_time = time() - N_of_points*20.0 # compensate for 20ms per point data acquisition.
        self.circular_buffers[b'main'].append(data)

        if time() - self.last_update_time > self.update_period:
            buff = self.circular_buffers[b'main'].get_last_N(int(1000*self.update_period/50.0))
            g_pointer = self.circular_buffers[b'history'].g_pointer
            self.history_vector[0,0] = time()
            self.history_vector[1,0] = self.pressure_upstream = mean(buff[0,:])
            self.history_vector[2,0] = self.pressure_downstream = mean(buff[1,:])
            self.history_vector[3,0] = self.pressure_barometric = mean(buff[2,:])
            self.history_vector[4,0] = self.temperature = mean(buff[3,:])
            self.circular_buffers[b'history'].append(self.history_vector)
            self.last_update_time  = time()


    def run(self):
        """"""
        from numpy import zeros
        self.history_vector = zeros((5,1))
        sleep(1)
        self.running = True
        self.last_update_time = time()
        while self.running:
            self.run_once()

            
##################################################################################################################
##################################################################################################################
######   ######
##################################################################################################################
##################################################################################################################
    


def init(msg_in = None, client = None):
    try:
        driver.ser.close()
    except:
        warn(traceback.format_exc())
    if 'di245_dl' in globals():
        global di245_dl,device_level
        del di245_dl,device_level
    di245_dl = DI245_DL()
    device_level = di245_dl
    return di245_dl.init()

di245_dl = device_level  = DI245_DL()

from XLI.drivers.DI245.serial_driver import driver

from XLI.server_LL import Server_LL
server = Server_LL()
server.init_server(name = 'DI245_DL', ports = [2040,2041,2042])


###Callback function linking between incoming server commands and functions in the DL
server.commands[b'init'] = init
server.commands[b'abort'] = di245_dl.abort
server.commands[b'close'] = di245_dl.close
server.commands[b'snapshot'] = di245_dl.snapshot
server.commands[b'controls'] = di245_dl.controls
server.commands[b'indicators'] = di245_dl.indicators
server.commands[b'notify_subscribers'] = di245_dl.notify_subscribers
server.commands[b'schedule'] = di245_dl.schedule
server.commands[b'get_circular_buffer'] = di245_dl.get_circular_buffer

server.commands[b'subscribe'] = server.subscribe

if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(#filename=gettempdir()+'/di245_DL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    self = di245_dl
    msg = 'DI4108 Data Acquisiion server is running. \n'
    msg += 'The server port %r and ip-address %r' %(server.port,server.ip_address)

    print(msg)
