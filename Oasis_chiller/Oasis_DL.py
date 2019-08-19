"""
Remote control of thermoelectric chiller by Solid State Cooling Systems,
www.sscooling.com, via RS-323 interface
Model: Oasis 160



"""
__version__ = '0.0.0'

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
        response[b'act_temperature'] = self.act_temperature
        response[b'fault'] = self.fault

        
        
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


    def get_act_temperature(self):
        try:
            response = device_level.circular_buffers['act_temperature'].get_last_N(1)[1]
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    act_temperature = property(get_act_temperature)

    def get_fault(self):
        try:
            response = driver.fault_description[int(device_level.circular_buffers['fault'].get_last_N(1)[1])]
        except:
            response = None 
            warn(traceback.format_exc())
        return response
    fault = property(get_fault)


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
        response[b'cmd_temperature'] = self.cmd_temperature
        response[b'idle_temperature'] = self.idle_temperature
        
        return response

    def set_cmd_temperature(self, value = 1):
        if device_level.soft_limits[b'lower']<= value <= device_level.soft_limits[b'upper']:
            device_level.cmd_temperature = value
            device_level.playlist.insert(device_level.playlist_counter,[time()+2,1,value])
        else:
            warn('Value %r is beyound soft limits (%r,%r) set on this device' %(value,device_level.soft_limits[b'low'],device_level.soft_limits[b'high']))
        
    def get_cmd_temperature(self):
        try:
            response = device_level.cmd_temperature
        except:
            response = None
            warn(traceback.format_exc())
        return response
    cmd_temperature = property(get_cmd_temperature,set_cmd_temperature)

    def set_idle_temperature(self, value = 1):
        device_level.idle_temperature = value
        
    def get_idle_temperature(self):
        try:
            response = device_level.idle_temperature
        except:
            response = None
            warn(traceback.format_exc())
        return response
    idle_temperature = property(get_idle_temperature,set_idle_temperature)

    def set_lower_limit(self, value = 1):
        device_level.lower_limit = value
        device_level.playlist.insert(device_level.playlist_counter,[time()+2,10,value])
        
    def get_lower_limit(self):
        try:
            response = device_level.lower_limit
        except:
            warn(traceback.format_exc())
            response = None
        return response
    lower_limit = property(get_lower_limit,set_lower_limit)

    def set_upper_limit(self, value = 1):
        device_level.upper_limit = value
        device_level.playlist.insert(device_level.playlist_counter,[time()+2,12,value])
        
    def get_upper_limit(self):
        try:
            response = device_level.upper_limit
        except:
            warn(traceback.format_exc())
            response = None
        return response
    upper_limit = property(get_upper_limit,set_upper_limit)

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

class Oasis_DL(XLevelTemplate):
    test = persistent_property('test', 'test')
    update_period = 2
    last_update_time = 0
    playlist = []
    circular_buffers = {}
    task_dictionary = {}
    idle_playlist = [[0,2,0]]+[[0,0,0]]*99
    default_playlist = [[0,2,0]]+[[0,0,0]]*10 
    idle_playlist_counter = 0
    playlist_counter = 0
    default_temperature = 8
    inds = Indicators()
    ctrls = Controls()
    circular_buffers = {}
    idle_temperature = 8.0

    soft_limits = {b'lower':2,b'upper':45}

    def setup_first_time(self):
        pass
    
    def init(self, msg_in = None, client = None):

        """
        initialize the DL program
        """
        self.name = 'Oasis_DL'

        self.circular_buffers[b'act_temperature'] = CBServer(size = (2,4320000), var_type = 'float64')
        self.circular_buffers[b'cmd_temperature'] = CBServer(size = (2,4320000), var_type = 'float64')
        self.circular_buffers[b'fault'] = CBServer(size = (2,10000), var_type = 'float64')

        self.description = ''

        self.task_dictionary[0] = {b'function':driver.get_actual_temperature,b'name':b'act_temperature'}
        self.task_dictionary[1] = {b'function':driver.set_target_temperature,b'name':b'cmd_temperature'}
        self.task_dictionary[2] = {b'function':driver.get_faults,b'name':b'fault'}
        


        self.task_dictionary[10] = {b'function':driver.set_lower_limit,b'name':b'set_lower_limit'}
        self.task_dictionary[11] = {b'function':driver.get_lower_limit,b'name':b'get_lower_limit'}
        self.task_dictionary[12] = {b'function':driver.set_upper_limit,b'name':b'set_upper_limit'}
        self.task_dictionary[13] = {b'function':driver.get_upper_limit,b'name':b'get_upper_limit'}

        flag = False
        message = None
        err = ''
        flag, message, err = driver.init(), '', ''
        if flag:
            self.lower_limit = driver.device_dict[b'lower_limit']
            self.upper_limit = driver.device_dict[b'upper_limit']

        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def abort(self, msg_in = {b'mode':b'idle_temperature'}, client = None):

        """
        abort current execution
        """
        if msg_in is not None:
            mode = msg_in[b'mode']
        else:
            mode = ''
        self.playlist = []
        self.playlist_counter = 0
        if mode == b'idle_temperature':
            self.ctrls.set_cmd_temperature(self.ctrls.idle_temperature)
            
        flag = True
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
        driver.close()
        
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
        flag = True
        message = {}
        try:
            message[b'description'] = self.description
            message[b'indicators'] = self.inds.get()
            message[b'controls'] = self.ctrls.get()
        except:
            err += traceback.format_exc()
            error(err)
            flag = False
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

    def schedule_task_queue(self, msg_in = {b'method':b'ramp',b'start_time':time()}, client = None):
    #build in schedule task queue function. See the class file for details
        flag = True
        message = None
        err = ''

        
        start_time = msg_in[b'start_time']
        method = msg_in[b'method']
        self.playlist = self.create_task_sequence(start_time = start_time); self.playlist_counter = 0;

        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response
        

    #def circular_buffer(self, msg_in = None, client = None):
    #build in get circular buffer function. See the class file for details    

##################################################################################################################
##################################################################################################################
######  Threading Section  ######
##################################################################################################################
##################################################################################################################
######
##################################################################################################################
    def start(self):
        from threading import Thread
        task = Thread(target=self.run,name="oasis_dl.run")
        task.daemon = True
        task.start()
        
    def stop(self):
        """
        
        """
        self.running = False

    def run_once(self):
        """
        """
        t = time()
        task = self.next_task(t = t)
        debug('task = %r, time = %r' %(task,time()))
        self.execute_task(lst = task)
        self.last_update_time = t

    def run(self):
        """"""
        from numpy import zeros
        self.running = True
        self.last_update_time = time()
        if len(self.idle_playlist) == 0:
            self.idle_playlist = self.default_playlist
        while self.running:
            t1 = time()
            self.run_once()
            t2 = time()
            sleep(self.update_period - (t2-t1))

    def next_task(self, t = 0):
        """
        returns next task that needs to be executed.

        Input:
            - t as current time
        """
        
        if self.idle_playlist_counter >= len(self.idle_playlist)-1:
            self.idle_playlist_counter = 0
        if len(self.playlist) ==0:
            task = self.idle_playlist[self.idle_playlist_counter]
            self.idle_playlist_counter +=1

        if self.playlist_counter < len(self.playlist):
            while self.playlist[self.playlist_counter][0] - t  < 0:
                self.playlist_counter +=1
            if abs(self.playlist[self.playlist_counter][0] - t ) < 2.0*1.1:
                task = self.playlist[self.playlist_counter]
                debug(task)
                self.playlist_counter +=1
            else:
                task = self.idle_playlist[self.idle_playlist_counter]
                self.idle_playlist_counter +=1
        else:
            task = self.idle_playlist[self.idle_playlist_counter]
            self.idle_playlist_counter +=1

        return task

    #def schedule(self, mode 

    def get_schedule_old(self, mode = '', start_time = 0):
        lst = []
        for i in range(10):
            lst.append([start_time+ 20*i,1,5+i])
        i += 5
        lst.append([start_time+ 20*i,1,5+i-5])
        for j in range(10):
            lst.append([start_time+ 20*i+ 20*j,1,5+i-5-j])
        lst.append([start_time+ + 20*i+ 20*j+20,1,5])
        return lst

    def create_task_sequence(self, mode = 'ramp', start_time = 0):
        def ramp(low = 8.0,high = 45.0, step = 1, hold_low = 4, hold_high = 6, \
                 wait = False, idle_temp = 8.0, start_time = time() + 10, time_step = 12, \
                 repeat = 1):
            lst = []
            for i in range(1,int((45-8)/step)):
                lst.append([start_time+ time_step*i,1,low+i*step])
                
            for j in range(1,int((45-8)/step)):
                lst.append([start_time+ time_step*i+time_step*hold_high + time_step*j,1,high-j*step])
            lst.append([start_time+ time_step*i+time_step*hold_high + time_step*j+time_step*hold_low ,1,idle_temp])
            return lst
        if mode == 'ramp':
            lst = ramp(start_time = start_time)
        else:
            lst = []
        return lst

    def execute_task(self, lst = [0,0,0]):
            from numpy import zeros
            if len(lst) != 0:
                res_arr = zeros((2,1))
                t_task = lst[0]
                task = lst[1]
                value = lst[2]

                value = self.task_dictionary[task][b'function'](value)
                res_arr[0,0] = time()
                res_arr[1,0] = value


                if task == 0:
                    self.circular_buffers[b'act_temperature'].append(res_arr)
                    self.act_temeprature = value
                    debug('%r get temperature executed: T = %r' %(time(),value))
                elif task == 1:
                    self.circular_buffers[b'cmd_temperature'].append(res_arr)
                    self.cmd_temperature = value
                    debug('%r set temperature executed: T = %r' %(time(),value))
                elif task == 2:
                    self.circular_buffers[b'fault'].append(res_arr)
                    self.fault = value
                    debug('%r get faults executed: T = %r' %(time(),value))


    def plot_circular_buffers(self, x_ext = nan, y_ext = nan):
        from matplotlib import pyplot as plt
        pointer = self.circular_buffers[b'act_temperature'].pointer
        buff = self.circular_buffers[b'act_temperature'].buffer
        x1 = buff[0,:pointer+1]
        y1 = buff[1,:pointer+1]
        plt.plot(x1,y1,'o')

        pointer = self.circular_buffers[b'cmd_temperature'].pointer
        buff = self.circular_buffers[b'cmd_temperature'].buffer
        x2 = buff[0,:pointer+1]
        y2 = buff[1,:pointer+1]
        plt.plot(x2,y2,'o')

        plt.plot(x_ext,y_ext,'o')
        plt.show()
        
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
        global oasis_dl,device_level
        del oasis_dl,device_level
    oasis_dl = Oasis_DL()
    device_level = oasis_dl
    return oasis_dl.init()

oasis_dl = device_level  = Oasis_DL()

from XLI.drivers.OasisChiller.serial_driver import driver

from XLI.server_LL import Server_LL
server = Server_LL()
server.init_server(name = 'OasisChiller_DL', ports = [2040,2041,2042])


###Callback function linking between incoming server commands and functions in the DL
server.commands[b'init'] = init
server.commands[b'abort'] = device_level.abort
server.commands[b'close'] = device_level.close
server.commands[b'snapshot'] = device_level.snapshot
server.commands[b'controls'] = device_level.controls
server.commands[b'indicators'] = device_level.indicators
server.commands[b'notify_subscribers'] = device_level.notify_subscribers
server.commands[b'schedule'] = device_level.schedule
server.commands[b'get_circular_buffer'] = device_level.get_circular_buffer

server.commands[b'subscribe'] = server.subscribe

if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(#filename=gettempdir()+'oasis_DL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    self = device_level
    msg = 'Oasis Chiller is running. \n'
    msg += 'The server port %r and ip-address %r' %(server.port,server.ip_address)

    print(msg)
    print('oasis_dl.init(); oasis_dl.start();')
    print('oasis_dl.playlist = oasis_dl.create_task_sequence(start_time = time()); oasis_dl.playlist_counter = 0;')
    print('oasis_dl.plot_circular_buffers()')
    print('oasis_dl.ctrls.set_cmd_temperature(7)')
    print("t1 = time(); res = oasis_dl.retrieve_values(msg_in = \
        {b'buffer_name':b'act_temperature', b'time_vector': asarray([time()-10,time()-20])}, N = 2);t2 = time(); t2-t1")
    print('for i in range(len(arr)):arr[i] = time() - 100 - i*4')
    from numpy import zeros
    arr = zeros(10)
    

