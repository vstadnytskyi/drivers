#!/bin/env python

"""Motion control GUI

Author: Valentyn Stadnytskyi
Date: March 16, 2018 -

version: 0.1

"""

#!/bin/env python
"""
High Pressure Apparatus System Level
create:
last modified: 12-21-17 by Valentyn Stadnytskyi
modification: added thread_measurement, EventDetector class added, Pulse generator class created

by Gabriel Anfinrud, Philip Anfinrud, Valentyn Stadnytskyi
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

#threading library manual https://docs.python.org/3/library/threading.html
#def round_sig(x,sig=4):   return round(x,sig-int(floor(log10(abs(x))))-1)
    
"""Graphical User Interface"""
        
class GUI(wx.Frame):
    
    def __init__(self):
        name = 'GUI'
        self.create_GUI()

        
        
    def create_GUI(self):
        
        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "ThorLabs Motor", pos = (0,0))#, style= wx.SYSTEM_MENU | wx.CAPTION)
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_THEME, pos = (0,0))

        
        
        ###########################################################################
        ##MENU for the GUI
        ###########################################################################
        file_item = {}
        about_item = {}
        self.calib_item = {}
        self.opt_item = {}
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        file_item[2] = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit, file_item[2])
               
        optMenu = wx.Menu()
        self.opt_item[0]= optMenu.Append(wx.NewId(),  'Advanced')
        self.Bind(wx.EVT_MENU, self.on_advanced, self.opt_item[0])

        
        aboutMenu = wx.Menu()
        about_item[0]= aboutMenu.Append(wx.ID_ANY,  'About')
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

        self.text =wx.StaticText(self.panel, label= "ThorLabs controller")
        sizer.Add(self.text , pos=(0, 0),  span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL, border=5)

        font=wx.Font(14,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        font2=wx.Font(32,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        
        
        self.Centre() 
        self.Show(True) 
    
        self.panel.SetSizer(sizer)

        gsizer = wx.BoxSizer(wx.VERTICAL)
        gsizer.Add(self.panel, 0)
        
        self.SetSizer(gsizer)
        self.Fit()

           
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
        wx.MessageBox('This is information about the high pressure control panel apparatus', 'High Pressure Apparatus', wx.OK | wx.ICON_INFORMATION)

    def on_quit(self,event):
        print('OnQuit pressed')
 
           
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
            self.text = wx.StaticText(self.panel, label= "Pulse Generator Options")
            sizer.Add(self.text , pos=(0, 0), span = (1,2), flag=wx.TOP|wx.RIGHT, border=5)

            
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

 
    
""" Main part of the progam """        
if __name__ == "__main__":
    app = wx.App(False)
    frame = GUI()
    frame.Show()
    app.MainLoop() 

    

	
