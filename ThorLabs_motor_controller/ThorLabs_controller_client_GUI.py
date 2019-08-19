#!/bin/env python

"""ThorLabs Motion control GUI

Author: Valentyn Stadnytskyi
Date: March 16, 2018 -

version: 0.1

"""

import psutil, os
#p = psutil.Process(os.getpid())
#p.nice(psutil.HIGH_PRIORITY_CLASS) #source: https://psutil.readthedocs.io/en/release-2.2.1/
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITY_CLASS
from time import time,sleep,clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime
import logging
from persistent_property import persistent_property

from threading import Thread
import thread
from socket import *
import logging
from logging import error,warn,info,debug
import logging
import msgpack
import msgpack_numpy as m
import h5py
from datetime import datetime
from math import log10, floor
from numpy import arange, asfarray, argmax, amax, amin, argmin, gradient, size, random, nan, inf, mean, std, asarray, where, array, concatenate, delete, shape, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max, savetxt, median
import wx # wxPython GUI library




__version__ = '0.1.0' #
__date__  = '03-16-2018'



from threading import Thread, Event, Timer, Condition
from thread import start_new_thread
from time import time, sleep
from persistent_property import persistent_property

#threading library manual https://docs.python.org/3/library/threading.html
#def round_sig(x,sig=4):   return round(x,sig-int(floor(log10(abs(x))))-1)
    
"""Graphical User Interface"""
        
class GUI(wx.Frame):
    
    #device_lst = persistent_property('intervention_enabled', False)
    
    def __init__(self):
        name = 'ThorLabsMotionControlGUI'
        self.create_GUI()
    
        
        
    def create_GUI(self):
        
        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "ThorLabs Motor", pos = (0,0))#, style= wx.SYSTEM_MENU | wx.CAPTION)
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_THEME, pos = (0,0))

        #self.statusbar = self.CreateStatusBar() # Will likely merge the two fields unless we can think of a reason to keep them split
        #self.statusbar.SetStatusText('This goes field one')
        #self.statusbar.SetStatusText('Field 2 here!', 1)
        #self.statusbar.SetBackgroundColour('green')
        
        file_item = {}
        about_item = {}
        self.calib_item = {}
        self.opt_item = {}
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        file_item[2] = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
 #       self.Bind(wx.EVT_MENU, self.OnQuit, file_item[2])
               
        optMenu = wx.Menu()
        self.opt_item[0]= optMenu.Append(wx.NewId(),  'Advanced')
        self.Bind(wx.EVT_MENU, self.on_advanced, self.opt_item[0])
        
        ###########################################################################
        ##MENU for the GUI
        ###########################################################################
        file_item = {}
        about_item = {}
        opt_item = {}
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        file_item[0] = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit, file_item[0])
               
        optMenu = wx.Menu()
        opt_item[0]= optMenu.Append(wx.NewId(),'Advanced')
        self.Bind(wx.EVT_MENU, self.on_advanced, opt_item[0])

        
        aboutMenu = wx.Menu()
        about_item[0]= aboutMenu.Append(wx.ID_ANY,'About')
        self.Bind(wx.EVT_MENU, self.on_about, about_item[0])
   
        
        menubar.Append(fileMenu, '&File')
        menubar.Append(optMenu, '&Options')
        menubar.Append(aboutMenu, '&About')
        
        
        self.SetMenuBar(menubar)
        #self.DicObjects[8].Bind(wx.EVT_BUTTON, self._on_calibration_press)
        
        
        
        self.Centre()
        self.Show(True)
        
        
        ###########################################################################
        ###MENU ENDS###
        ###########################################################################
        

        ###########################################################################
        ###On Button Press###
        ###########################################################################
        sizer = wx.GridBagSizer(hgap = 5, vgap = 5)#(13, 11)
        

        ######
 #       self.ip_dropdown_list = [['164.54.161.34','128.231.5.78','127.0.0.1'],['APS','NIH','localhost']] 
#        self.IP_choice = wx.Choice(self.panel,choices = self.ip_dropdown_list[1][:])
#        self.IP_choice.SetSelection(self.environment)
#        self.IP_choice.Bind(wx.EVT_CHOICE, self._on_change_ip_press)
#        sizer.Add(self.IP_choice, pos=(0, 1), span=(1, 1), flag=wx.TOP|wx.EXPAND, border=5) 

        self.text = wx.StaticText(self.panel, label= "ThorLabs controller")
        sizer.Add(self.text , pos=(0, 0),  span=(1,3), flag=wx.ALIGN_CENTER_VERTICAL, border=5)

        self.button_dev_connect = wx.Button(self.panel,  label = 'connect')
        sizer.Add(self.button_dev_connect, pos = (1,0), span = (1,2))
        self.button_dev_connect.Bind(wx.EVT_BUTTON,self.on_dev_connect)
        self.button_dev_disconnect = wx.Button(self.panel,  label = 'disconnect')
        sizer.Add(self.button_dev_disconnect, pos = (1,2), span = (1,2))
        self.button_dev_disconnect.Bind(wx.EVT_BUTTON,self.on_dev_disconnect)

        self.button_go_plus = wx.Button(self.panel,size = (50,-1),  label = '+')
        sizer.Add(self.button_go_plus, pos = (4,0), span = (1,1))
        self.button_go_plus.Bind(wx.EVT_BUTTON,self.on_plus_button)

        self.button_go_minus = wx.Button(self.panel, size = (50,-1),  label = '-')
        sizer.Add(self.button_go_minus, pos = (4,1), span = (1,1))
        self.button_go_minus.Bind(wx.EVT_BUTTON,self.on_minus_button)
        
        self.button_home = wx.Button(self.panel, size = (50,-1),  label = 'home')
        sizer.Add(self.button_home, pos = (4,2), span = (1,1))
        self.button_home.Bind(wx.EVT_BUTTON,self.on_home_button)

        self.button_goto = wx.Button(self.panel, size = (50,-1),  label = 'go to')
        sizer.Add(self.button_goto, pos = (4,3), span = (1,1))
        self.button_goto.Bind(wx.EVT_BUTTON,self.on_goto_button)

 #       self.button_home = wx.Button(self.panel, size = (50,-1),  label = 'home')
 #       sizer.Add(self.button_home, pos = (4,0), span = (1,1))

        self.text_position = wx.StaticText(self.panel, size = (50,-1), label="position")
        sizer.Add(self.text_position, pos = (2,0), span = (1,1))
        
        self.indicator_position = wx.StaticText(self.panel)#, size = (50,-1))
        self.indicator_position.SetLabel(str(nan))
        sizer.Add(self.indicator_position, pos = (2,1), span = (1,2))
        self.Bind(wx.EVT_TEXT, self.on_position_typed, self.indicator_position)

        self.control_position = wx.TextCtrl(self.panel)#, size = (50,-1))
        self.control_position.SetLabel(str(nan))
        sizer.Add(self.control_position, pos = (2,3), span = (1,2))
        self.Bind(wx.EVT_TEXT, self.on_position_typed, self.control_position)

        self.text_error = wx.StaticText(self.panel, size = (50,-1), label="error")
        sizer.Add(self.text_error, pos = (3,0), span = (1,1))
        
        self.indicator_error = wx.TextCtrl(self.panel)#, size = (50,-1))
        self.indicator_error.SetValue(str(None))
        sizer.Add(self.indicator_error, pos = (3,1), span = (1,3))

        
        
    

        self.text_information = wx.TextCtrl(self.panel, size = (300,200), value= "Information:")
        sizer.Add(self.text_information, pos = (5,0), span = (4,4))

        
        font=wx.Font(14,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        font2=wx.Font(32,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        
        
        self.Centre() 
        self.Show(True) 
    
        self.panel.SetSizer(sizer)

        gsizer = wx.BoxSizer(wx.VERTICAL)
        gsizer.Add(self.panel, 0)
        
        self.SetSizer(gsizer)
        self.Fit()

        
        self.position_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_position_timer, self.position_timer)
        self.position_timer.Start(1000)

           
    ###########################################################################
    ###On Button Press###
    ###########################################################################
    def on_target_pressure_after_typed(self,event):
        try:
            EventDetector.coeffTargetPressure = float(event.GetString())
        except:
            pass               
        ###########################################################################
        ###END: On Button Press###
        ###########################################################################
            

        
    def on_about(self,event):
        wx.MessageBox('ThorLabs motor control', 'ThorLabs motor control', wx.OK | wx.ICON_INFORMATION)

    def on_quit(self,event):
        print('OnQuit pressed')
 
    def on_position_enter(self,event):
        print('position entered')


        
    class AdvanceWindowFrame(wx.Frame):
        title = "Advance Options"

        def __init__(self):
            
            self.advanceFrame = wx.Frame.__init__(self, None, wx.ID_ANY, title=self.title, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
            self.panel=wx.Panel(self, -1)

            self.initGUI()
            self.SetBackgroundColour(wx.Colour(255,255,255))
            self.Centre()
            self.Show()

        def initGUI(self):
            sizer = wx.GridBagSizer(hgap = 5, vgap = 5)

            ###Pulse Generator Options
            self.text = wx.StaticText(self.panel, label= "Settings")
            sizer.Add(self.text , pos=(0, 0), span = (1,2), flag=wx.TOP|wx.RIGHT, border=5)

            self.text_physical_name = wx.StaticText(self.panel, size = (100,-1), label="Physical Name")
            sizer.Add(self.text_physical_name, pos = (1,0), span = (1,1))
            self.control_physical_name = wx.TextCtrl(self.panel)#, size = (50,-1))
            self.control_physical_name.SetLabel(str(nan))
            sizer.Add(self.control_physical_name, pos = (1,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_serial_number = wx.StaticText(self.panel, size = (100,-1), label="Serial Number")
            sizer.Add(self.text_serial_number, pos = (2,0), span = (1,1))
            self.control_serial_number  = wx.TextCtrl(self.panel)#, size = (50,-1))
            self.control_serial_number.SetLabel(str(nan))
            sizer.Add(self.control_serial_number, pos = (2,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_location = wx.StaticText(self.panel, size = (100,-1), label="Location")
            sizer.Add(self.text_location, pos = (3,0), span = (1,1))
            self.control_location = wx.TextCtrl(self.panel)#, size = (50,-1))
            self.control_location.SetLabel(str(nan))
            sizer.Add(self.control_location, pos = (3,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_motor = wx.StaticText(self.panel, size = (100,-1), label="motor")
            sizer.Add(self.text_motor, pos = (4,0), span = (1,1))
            self.control_motor = wx.TextCtrl(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.motor
            except:
                string = None
            self.control_motor.SetLabel(str(string))
            sizer.Add(self.control_motor, pos = (4,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_soft_limits = wx.StaticText(self.panel, size = (100,-1), label="Soft_limits")
            sizer.Add(self.text_soft_limits, pos = (5,0), span = (1,1))
            self.control_soft_limits_l = wx.TextCtrl(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.soft_limits[0]
            except:
                string = None
            self.control_soft_limits_l.SetLabel(str(string))
            sizer.Add(self.control_soft_limits_l, pos = (5,1), span = (1,1))
            self.control_soft_limits_h = wx.TextCtrl(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.soft_limits[1]
            except:
                string = None
            self.control_soft_limits_h.SetLabel(str(string))
            sizer.Add(self.control_soft_limits_h, pos = (5,2), span = (1,1))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_gear_ratio = wx.StaticText(self.panel, size = (100,-1), label="Gear Ratio")
            sizer.Add(self.text_gear_ratio, pos = (6,0), span = (1,1))
            self.control_gear_ratio = wx.TextCtrl(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.gear_ratio
            except:
                string = None
            self.control_gear_ratio.SetLabel(str(string))
            sizer.Add(self.control_gear_ratio, pos = (6,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            
            self.text_position = wx.StaticText(self.panel, size = (100,-1), label="Position")
            sizer.Add(self.text_position, pos = (7,0), span = (1,1))
            self.control_position = wx.StaticText(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.cur_position
            except:
                string = None
            self.control_position.SetLabel(str(string))
            sizer.Add(self.control_position, pos = (7,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)

            self.text_client = wx.StaticText(self.panel, size = (100,-1), label="Client")
            sizer.Add(self.text_client, pos = (8,0), span = (1,1))
            self.control_client = wx.StaticText(self.panel)#, size = (50,-1))
            try:
                string = frame.dev.last_client_request
            except:
                string = None
            self.control_client.SetLabel(str(string))
            sizer.Add(self.control_client, pos = (8,1), span = (1,2))
            #self.Bind(wx.EVT_TEXT, self.on_control_motor_typed, self.control_motor)



 

            
            self.panel.SetSizer(sizer)

            gsizer = wx.BoxSizer(wx.VERTICAL)
            gsizer.Add(self.panel, 0)
            
            self.SetSizer(gsizer)
            self.Fit()
            
    ### Advanced Options
    def on_advanced(self,event):
        print("Clicked")
        self.AdvanceWindow = self.AdvanceWindowFrame()
        self.AdvanceWindow.Show()

    
    ###########################################################################
    ###END: On Button Press###
    ###########################################################################


    #####################################
    ###Methods
    ######################################

    def on_plus_button(self,event):
        try:
            self.dev.move_forward(1)
        except:
            text_information.SetLabel('device is not connected') 


    def on_minus_button(self,event):
        try:
            self.dev.move_backward(1)
        except:
            text_information.SetLabel('device is not connected')        
            
    def on_goto_button(self,event):
        try:
            value = float(self.new_position)
            print('goto value = %r' % value)
            result = self.dev.move_abs(value)
            print(result)
            if result[0]:
                string = self.indicator_position.GetLabel() + '->' + str(self.new_position)
                self.indicator_position.SetLabel(string)
            else:
                string = str(self.dev.get_position())
                self.indicator_position.SetLabel(string)
            self.indicator_error.SetValue(str(result[1]))
        except Exception as err_msg:
            error(err_msg)
            self.text_information.SetLabel('device is not connected')

    def on_home_button(self,event):
        try:
            self.new_position = 'home'
            self.dev.home()
            string = self.indicator_position.GetLabel() + '->' + str(self.new_position)
            self.indicator_position.SetLabel(string)
        except:
            text_information.SetLabel('device is not connected')        

    def on_get_position(self,event):
        try:
            value = self.dev.get_position()
        except:
            self.text_information.SetLabel('device is not connected')
            value = nan
        return value
    
    def on_position_timer(self,event):
        value = self.on_get_position(None)
        self.indicator_position.SetLabel(str(value))
        
    def get_information(self,event):
        try:
            string = 'Information: \n' + self.dev.get_information()
            self.text_information.SetLabel(string)
        except:
            self.text_information.SetLabel('device is not connected')
            
    def on_dev_connect(self,event):
        self.dev = motion_controller('SampleR')
        self.get_information(None)

    def on_dev_disconnect(self,event):
        del self.dev


    def on_position_typed(self, event):
        try:
            self.new_position = float(event.GetString())
            print('new position %r' % self.new_position)
        except:
            pass
        
class motion_controller(object):
    cur_position = persistent_property('cur_position', nan)
    serial_number = persistent_property('serial_number', 0)
    motor = persistent_property('motor', 'test')
    controller = persistent_property('controller', 'test')
    soft_limits = persistent_property('soft_limits', (nan,nan))
    gear_ratio = persistent_property('gear_ratio', nan)
    last_client_request = persistent_property('last_client_request', nan)
    def __init__(self, name):
        self.name = name
        debug('motion control has been initialized')
        #self.cur_position = 0.0
        self.serial_number = 83830000
        self.motor = 'test'
        self.controller = 'test'
        self.soft_limits = (-10.0,10.0)
        self.gear_ratio = 100
        self.last_client_request = 'localhost'

    def is_connected(self):
        pass

    def move_abs(self,pos):
        if pos <= self.soft_limits[1] and pos >= self.soft_limits[0]:
            self.cur_position = pos
            res = (True,'None')
        else:
            res = (False,'soft limits')
        return res    
            

    def move_forward(self,step):
        debug('move forward by %r' % step)
        self.cur_position = self.cur_position + step

    def move_backward(self,step):
        debug('move backward by %r' % step)
        self.cur_position = self.cur_position - step    

    def get_position(self):
        return self.cur_position

    def get_information(self):
        return 'This is test information \n regarding a connected test device'

    def home(self):
        self.cur_position = 0.0

        
""" Main part of the progam """

if __name__ == "__main__":
    logging.basicConfig(filename='ThorLabsGUI.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
    debug('This message should go to the log file')
    info('So should this')
    warn('And this, too')
    app = wx.App(False)
    frame = GUI()
    frame.Show()
    app.MainLoop() 

    

	
