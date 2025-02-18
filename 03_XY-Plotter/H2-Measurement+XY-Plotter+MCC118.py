#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
#########################################################################################
#
#BSD 3-Clause License
#
#Copyright (c) 2025, Leibniz Institute for Materials Engineering - IWT,
#                    Norbert Riefler <riefler@iwt.uni-bremen.de>
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################################
"""
    MCC 118 Functions Demonstrated:
        mcc118.t_in_read

    Purpose:
        Read a single data value for each channel in a loop.

    Description:
        This example demonstrates acquiring data using a software timed loop
        to read a single value from each selected channel on each iteration
        of the loop.

    Program written by Norbert Riefler, Leibniz-IWT Bremen


"""
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, chan_list_to_mask

import tkinter
import tkinter.font
from tkinter import filedialog

import datetime

#tools for calculations + plotting:
import numpy as np
import matplotlib.pyplot as plt

import os


#Change to the data directory:
os.chdir('/home/pi/Data')



#####################################################################################################
#####################################################################################################
#####################################################################################################
class ControlApp:

  ###################################################################################################
  ###################################################################################################
  ###################################################################################################
  def __init__(self, master):
    self.master = master
    master.title("Data Acquisition")

    #################################################################################################
    # Calibrate voltage measurements - H2 concentration
    #
    # 1. Simple linear range:
    # minimal value of 0% H2 corresponds to 4 mA:
    self.U_min=2.2075 #V
    # maximum value of 100% H2 corresponds to 20 mA:
    self.U_max=9.1539 #V
    # conversion:
    # U_min <> H_2_min=0%
    # U_max <> H_2_max=100%
    # U_x   <> H_2=x%
    #   =>
    # x%=(U_x-U_min)/(U_max-U_min)*H_2_max
    #
    #Fantasie-Werte zur Darstellung des Eigenrauschens offener Eigaenge:
    self.U_min=1.65 #V
    self.U_max=1.9 #V
    #################################################################################################
    
    
    
    
    #################################################################################################
    # Initialize variables
    self.device_open = False
    self.open_address = 0
    self.board = None
    self.job = None
    #################################################################################################
    
    
    
    
    #################################################################################################
    # GUI Setup
    self.bold_font = tkinter.font.Font(
      family=tkinter.font.nametofont("TkDefaultFont")["family"],
      size=tkinter.font.nametofont("TkDefaultFont")["size"],
      weight="bold")
    #
    # Create and organize frames:
    #Top Frame:
    self.top_frame = tkinter.LabelFrame(master, text="Start/Stop Storage")
    self.top_frame.pack(expand=True, fill=tkinter.BOTH)
    #
    #Mid Frame: (not used here)
    #self.mid_frame = tkinter.LabelFrame(master, text="mid_frame")
    #self.mid_frame.pack(expand=False, fill=tkinter.X)
    #self.mid_frame.grid_columnconfigure(1, weight=1)
    #
    #Bottom Frame: (not used here)
    #self.bottom_frame = tkinter.LabelFrame(master, text="Temperatur-Inputs")
    #self.bottom_frame.pack(expand=True, fill=tkinter.BOTH)
    #self.bottom_frame.grid_columnconfigure(1, weight=1)
    #self.bottom_frame.grid_columnconfigure(2, weight=1)
    #
    #self.bottom_frame.bind("<Configure>", self.resize_text)
    #
    # Create widgets:
    self.dev_label = tkinter.Label(self.top_frame, text="Save Button:")
    self.dev_label.grid(row=0, column=0)
    #create save button:
    self.save_button = tkinter.Button(self.top_frame, text="Click_to_save_in_file", width=20, command=self.pressed_save_button)
    self.save_button.grid(row=0, column=2)
    #################################################################################################




    #################################################################################################
    #MCC118 SETUP
    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    #channels = [0, 1, 2, 3]
    #channels = [0, 1]
    channels = [0]
    self.channel_mask = chan_list_to_mask(channels)
    self.num_channels = len(channels)

    self.samples_per_channel = 0

    self.total_samples_read = 0
    #self.read_request_size = READ_ALL_AVAILABLE

    self.options = OptionFlags.CONTINUOUS
    #self.options = OptionFlags.DEFAULT

    #self.scan_rate = 2.0 #seconds for one scan
    self.scan_rate = 1.0 #seconds for one scan
    #self.scan_rate = 0.5 #seconds for one scan FUNZT NED!

    #
    address = select_hat_device(HatIDs.MCC_118)
    #print(address)
    self.board = mcc118(address)
    #print(self.board)


    print('\nSelected MCC 118 HAT device at address', address)


    #deactivate previous instance:
    self.board.a_in_scan_stop()
    self.board.a_in_scan_cleanup()

    self.actual_scan_rate = self.board.a_in_scan_actual_rate(self.num_channels, self.scan_rate)

    self.board.a_in_scan_start(self.channel_mask, self.samples_per_channel, self.scan_rate,self.options)

    # When doing a continuous scan, the timeout value will be ignored in the
    # call to a_in_scan_read because we will be requesting that all available
    # samples (up to the default buffer size) be returned.
    self.timeout = 5.0
    #################################################################################################




    #################################################################################################
    #Matplotlib SETUP:
    #
    #Extend figure to full screen size: -> NOT REASONABLE
    #root = tkinter.Tk()
    #self.screen_width = root.winfo_screenwidth()
    #self.screen_height = root.winfo_screenheight()    
    #little smaller:
    #self.screen_width = self.screen_width-round(self.screen_width/10)
    #self.screen_height = self.screen_height-round(self.screen_height/10)
    #print("self.screen_width="+str(self.screen_width)+", self.screen_height="+str(self.screen_height)) 
    
    self.fig = plt.figure(1,figsize=(10, 5), dpi=100)#<>figure with 1000x400 pixels
    self.fig.clear()
    self.ax1=self.fig.add_subplot(2,1,1)
    self.ax2=self.fig.add_subplot(2,1,2)
    #logarithmic scale / logarithmische Skalierung:
    #ax1.set_yscale('log')
    #
    self.ax1.grid(True)
    self.ax1.set(ylabel='Voltage [V]')#no xlabel because it is on ax2
    self.ax1.grid(True)
    #
    self.ax2.grid(True)
    self.ax2.set(xlabel='sample [-]', ylabel='conc. [%]')
    self.ax2.grid(True)
    
    self.index_plot = 0
    
    #IMPORTANT: n_results determines the number of measured points shown in the diagram
    n_results=50
    #allocation of the vectors:
    self.data_1=np.ones(n_results)*(self.U_max+self.U_min)/2
    self.data_2=np.zeros(n_results)
    self.total_samples=np.zeros(n_results)
    #################################################################################################



    #Allocate string for file saving:
    self.textLine=np.zeros(np.size(channels))
    #print(self.textLine)


    try:
      self.update_inputs()
    except KeyboardInterrupt:
      # Clear the '^C' from the display.
      print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')
      print('Stopping')
      self.board.a_in_scan_stop()
      self.board.a_in_scan_cleanup()
    

  ###################################################################################################
  # end of "def __init__(self, master):" ############################################################
  ###################################################################################################




  ###################################################################################################
  def resize_text(self, _):
    """ Resize event """
    height = self.bottom_frame.winfo_height()
    #new_size = -max(12, int(height / 7))
    new_size = -max(12, int(height / 7))
    #new_size = -max(12, int(event.height / 8))
    self.bold_font.configure(size=new_size)
  ###################################################################################################




  ###################################################################################################
  def update_inputs(self):
    #
    #routine to close program:
    try:
      read_result = self.board.a_in_scan_read(-1,5.0)
      print(read_result)
    except KeyboardInterrupt:
      # Clear the '^C' from the display.
      print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')
      print('Stopping')
      self.board.a_in_scan_stop()
      self.board.a_in_scan_cleanup()
    #read_request_size = READ_ALL_AVAILABLE
    #read_result = self.board.a_in_scan_read(-1,5.0)
    #print(read_result)

    ## Check for an overrun error
    #if read_result.hardware_overrun:
    #  print('\n\nHardware overrun\n')
    #  break
    #elif read_result.buffer_overrun:
    #  print('\n\nBuffer overrun\n')
    #  break
    
    samples_read_per_channel = int(len(read_result.data) / self.num_channels)
    self.total_samples_read += samples_read_per_channel

    # Display the last sample for each channel.
    #print('\r{:12}'.format(samples_read_per_channel),
    #      ' {:12} '.format(self.total_samples_read), end='')
    #
    index = samples_read_per_channel * self.num_channels - self.num_channels
    print("index="+str(index))
    #
    for ii in range(self.num_channels):
      #print('{:10.5f}'.format(read_result.data[index+ii]), 'V ',end='')
      if ii == 0:
        self.index_plot+=1
        print("self.index_plot="+str(self.index_plot))	
        H2=read_result.data[index+ii]
        #print("H2="+str(H2)+"V")
        #
        #conversion to H2 percentage
        H2_precentage_0=(read_result.data[index+ii]-self.U_min)/(self.U_max-self.U_min)*100
        #
        self.data_1[:-1] = self.data_1[1:]
        self.data_1[-1]=H2
        #
        self.data_2[:-1] = self.data_2[1:]
        self.data_2[-1]=H2_precentage_0
        #
        self.total_samples[:-1]=self.total_samples[1:]
        #self.total_samples[-1]=self.total_samples_read
        self.total_samples[-1]=self.index_plot
        print("self.total_samples="+str(self.total_samples)+"\n")
        print("self.data_1="+str(self.data_1)+"\n")
        #
        self.fig.clear()
        self.ax1=self.fig.add_subplot(2,1,1)
        self.ax2=self.fig.add_subplot(2,1,2)
        self.ax1.set(ylabel='Voltage [V]',title='H2 Measurements')
        self.ax1.grid(True)
        self.ax2.set(xlabel='sample [-]', ylabel='conc. [%]')
        self.ax2.grid(True)
        #plot voltage:
        self.ax1.plot(self.total_samples,self.data_1,'ro')
        #plot concentration:
        self.ax2.plot(self.total_samples,self.data_2,'go')
      #elif ii == 1:
        #CHANNEL NOT USED, see 'channels = [0]'
      #elif ii == 2:
        #CHANNEL NOT USED, see 'channels = [0]'
      #elif ii == 3:
        #CHANNEL NOT USED, see 'channels = [0]'
      #
      self.textLine[ii]=read_result.data[index+ii]
    
    stdout.flush()
    #print(self.textLine)
    #
    plt.show(block=False)
    plt.pause(0.1)
    self.fig.clf()

    #sleep(0.01)
    #Prepare for file storage:
    if self.save_button.cget('text') == "Save_in_Action":
      #prepare for readable output:
      tmp=str(self.textLine)
      tmp=tmp.replace('[', '')
      tmp=tmp.replace(']', '')
      tmp=tmp.replace("'", "")
      date=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
      lineInformation=date+', '+tmp+', '+str("{:1.3f}".format(H2_precentage_0))+'\n'
      self.outfile.write(lineInformation)
      #self.outfile.write(str(self.textLine)+'\n')
    #
    self.job = self.master.after(int(float(self.scan_rate)*1000), self.update_inputs)
  ###################################################################################################




  ###################################################################################################
  #Event (=pressed "Click_to_save_in_file"-button) handler:
  def pressed_save_button(self):
    if self.save_button.cget('text') == "Click_to_save_in_file":
      print('start saving')
      #filename = filedialog.asksaveasfilename(defaultextension=".txt")
      filename = filedialog.asksaveasfilename()
      if filename:  # user selected file
        filename=filename+"_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+".txt"
        self.outfile=open(filename,'w')
        self.outfile.write("date,                voltage,     H2-concentration\n")
        #fob.close()
      else: # user cancel the file browser window
        print("No file chosen")        #entry_window = tkinter.Tk()
      self.save_button.config(text="Save_in_Action")
    elif self.save_button.cget('text') == "Save_in_Action":
      print('stop saving and close file')
      self.save_button.config(text="Click_to_save_in_file")
      self.outfile.close()
  ###################################################################################################


#####################################################################################################
# end of "class ControlApp:" ########################################################################
#####################################################################################################





root = tkinter.Tk()
_app = ControlApp(root)
root.mainloop()






