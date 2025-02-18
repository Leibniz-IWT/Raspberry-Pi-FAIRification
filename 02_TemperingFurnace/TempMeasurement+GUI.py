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
    MCC 134 Functions Demonstrated:
        mcc134.t_in_read

    Purpose:
        Read a single data value for each channel in a loop.

    Description:
        This example demonstrates acquiring data using a software timed loop
        to read a single value from each selected channel on each iteration
        of the loop.
"""
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc134, HatIDs, HatError, TcTypes
from daqhats_utils import select_hat_device, tc_type_to_string

import tkinter
import tkinter.font
from tkinter import filedialog

import datetime

import os


os.chdir('/home/pi/Messdaten') 



#####################################################################################################
#####################################################################################################
#####################################################################################################
class ControlApp:

  #####################################################################################################
  #####################################################################################################
  #####################################################################################################
  def __init__(self, master):
      self.master = master
      master.title("Temperature Aquisition + ELN Upload")
      
      #N.R.: Save temperatures:
      #-> see "def pressed_save_button(self):" for save routine
      
      # Initialize variables
      self.device_open = False
      self.open_address = 0
      self.board = None
      self.job = None
      #N.R.:
      #Allocate string for file saving:
      self.textLine=['0','0','0','0']

      # GUI Setup
      self.bold_font = tkinter.font.Font(
          family=tkinter.font.nametofont("TkDefaultFont")["family"],
          size=tkinter.font.nametofont("TkDefaultFont")["size"],
          weight="bold")

      # Create and organize frames
      self.top_frame = tkinter.LabelFrame(master, text="Start/Stop Speicherung")
      self.top_frame.pack(expand=True, fill=tkinter.BOTH)

      self.mid_frame = tkinter.LabelFrame(master, text="TC Typen")
      self.mid_frame.pack(expand=False, fill=tkinter.X)

      self.bottom_frame = tkinter.LabelFrame(master, text="Temperatur-Inputs")
      self.bottom_frame.pack(expand=True, fill=tkinter.BOTH)

      # Create widgets
      self.dev_label = tkinter.Label(self.top_frame, text="MCC 134 address:")
      self.dev_label.grid(row=0, column=0)
      #create save button:
      self.save_button = tkinter.Button(self.top_frame, text="Click_to_save_in_file", width=20, command=self.pressed_save_button)
      self.save_button.grid(row=0, column=2)
      #print(self.save_button.cget('text'))
      #self.save_button.config(text="Close")
      #print(self.save_button.cget('text'))
      #
      self.mid_frame.grid_columnconfigure(1, weight=1)
      #
      self.bottom_frame.grid_columnconfigure(1, weight=1)
      self.bottom_frame.grid_columnconfigure(2, weight=1)
      #
      self.bottom_frame.bind("<Configure>", self.resize_text)
      #
      #create input field
      #top = self.top = tkinter.Toplevel(master)
      #self.myLabel = tkinter.Label(top, text='Enter Sample Name')
      #self.myLabel.pack()
      #self.myEntryBox = tkinter.Entry(top)
      #self.myEntryBox.focus_set()
      #self.myEntryBox.pack()
      #self.mySubmitButton = tkinter.Button(top, text='OK', command=self.DestWin)
      #self.mySubmitButton.pack()

      #
      address = select_hat_device(HatIDs.MCC_134)
      #print(address)
      self.board = mcc134(address)
      #print(self.board)
      
      #This loop runs first for initialization:
      self.channel_labels = []
      self.tc_type_options = []
      self.temperatures = []
      self.tc_type_vars = []
      tc_choices = ("J", "K", "T", "E", "R", "S", "B", "N", "Disabled")
      for index in range(mcc134.info().NUM_AI_CHANNELS):
          # TC types and labels
          label = tkinter.Label(self.mid_frame, text="Ch {}".format(index))
          label.grid(row=index, column=0)

          self.tc_type_vars.append(tkinter.StringVar(self.mid_frame))
          self.tc_type_vars[index].set(tc_choices[3])
          self.tc_type_options.append(
              tkinter.OptionMenu(
                  self.mid_frame, self.tc_type_vars[index], *tc_choices))
          self.tc_type_options[index].grid(row=index, column=1)
          self.tc_type_options[index].grid_configure(sticky="E")

          # Labels
          self.channel_labels.append(tkinter.Label(
              self.bottom_frame, text="Ch {}".format(index), font=self.bold_font))
          self.channel_labels[index].grid(row=index, column=1)
          self.channel_labels[index].grid_configure(sticky="W")
          # Temperatures
          self.temperatures.append(tkinter.Label(
              self.bottom_frame, text="0.00", font=self.bold_font))
          self.temperatures[index].grid(row=index, column=3)
          self.temperatures[index].grid_configure(sticky="E")

          self.bottom_frame.grid_rowconfigure(index, weight=1)
      #
      #Set the type of thermocouple
      self.board.tc_type_write(0, TcTypes.TYPE_K)
      self.tc_type_vars[0].set(tc_choices[1])
      self.board.tc_type_write(1, TcTypes.TYPE_J)
      self.tc_type_vars[1].set(tc_choices[0])
      self.board.tc_type_write(2, TcTypes.TYPE_T)
      self.tc_type_vars[2].set(tc_choices[2])
      self.board.tc_type_write(3, TcTypes.TYPE_S)
      self.tc_type_vars[3].set(tc_choices[5])
      
      self.update_inputs()

  #
  #    self.open_button = tkinter.Button(
  #        self.top_frame, text="Open", width=6, command=self.pressed_open_button)
  #
  #    # Get list of MCC 134 devices for the device list widget
  #    self.addr_list = self.list_devices()
  #####################################################################################################
  # end of "def __init__(self, master):" ##############################################################
  #####################################################################################################




  #####################################################################################################
  def resize_text(self, _):
      """ Resize event """
      height = self.bottom_frame.winfo_height()
      #new_size = -max(12, int(height / 7))
      new_size = -max(12, int(height / 7))
      #new_size = -max(12, int(event.height / 8))
      self.bold_font.configure(size=new_size)
  #####################################################################################################
  
  
  
  
  #####################################################################################################
  def update_inputs(self):
      """ Periodically read the inputs, save in a textline and update the display """
      # Read the enabled channels
      for channel in range(mcc134.info().NUM_AI_CHANNELS):
        value = self.board.t_in_read(channel)
        if value == mcc134.OPEN_TC_VALUE:
            text = "Open"
        elif value == mcc134.OVERRANGE_TC_VALUE:
            text = "Overrange"
        elif value == mcc134.COMMON_MODE_TC_VALUE:
            text = "Common mode error"
        else:
            text = "{:.4f}".format(value)
        self.temperatures[channel].config(text=text)
        self.textLine[channel]=str(text)+" "
      #N.R.: Prepare for file storage:
      if self.save_button.cget('text') == "Save_in_Action":
        #prepare for readable output:
        tmp=str(self.textLine)
        tmp=tmp.replace('[', '')
        tmp=tmp.replace(']', '')
        tmp=tmp.replace("'", "")
        date=datetime.datetime.now().strftime("%Y-%m_%d-%H-%M-%S")
        lineInformation=date+', '+tmp+'\n'
        self.outfile.write(lineInformation)
        #self.outfile.write(str(self.textLine)+'\n')
      #
      # call this every second
      #self.job = self.master.after(1000, self.update_inputs)
      # call this every 2th second
      self.job = self.master.after(2000, self.update_inputs)
      # call this every 5th second
      #self.job = self.master.after(5000, self.update_inputs)
  #####################################################################################################
  
  
  
  
  #####################################################################################################
  #Event (=pressed "Click_to_save_in_file"-button) handler:
  def pressed_save_button(self):
    if self.save_button.cget('text') == "Click_to_save_in_file":
      print('start saving')
      #filename = filedialog.asksaveasfilename(defaultextension=".txt")
      filename = filedialog.asksaveasfilename()
      if filename:  # user selected file
        filename=filename+"_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+".txt"
        self.outfile=open(filename,'w')
        self.outfile.write("Temperaturkurve des Nabertherm-Anlass-Ofens\n\n")
        #fob.close()
      else: # user cancel the file browser window
        print("No file chosen")        #entry_window = tkinter.Tk()
      #entry_window.title("Enter sample name")
      ##mystring =tkinter.StringVar(entry_window)
      ##def getvalue():
      ##  print(mystring.get())
      ##
      ##L1 = tkinter.Label(top, text="Label")
      ##top = tkinter.LabelFrame(top, text="Start/Stop Speicherung")
      ##L1 = tkinter.LabelFrame(top, text="Label")
      ##L1.pack(side=LEFT)
      #E1 = tkinter.Entry(entry_window,textvariable = mystring,width=100,fg="blue",bd=3,selectbackground='violet').pack()
      #E1 = tkinter.Entry(entry_window,show=None,font=('Arial',15))
      #entry=tkinter.Entry(entry_window,width=50,font=('Arial',15)).pack()
      #def get_value(guess):
      #  guess = entry.get()
      #  return guess # Replace this with the actual processing.
      #button = tkinter.Button(entry_window, text="OK", command=get_value).pack()
      ##def on_button(self):
      ##  print(self.mystring.get())
      ##tmp=E1.pack()
      #
      ##
      #self.filename = "TemperaturKurve_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+".txt"
      #self.filename = "tmp.txt"
      #print('Filename: '+str(filename))
      #self.outfile = open(filename, 'w')
      #self.outfile = open(sample_name, 'w')
      self.save_button.config(text="Save_in_Action")
    elif self.save_button.cget('text') == "Save_in_Action":
      print('stop saving and close file')
      self.save_button.config(text="Click_to_save_in_file")
      self.outfile.close()
    #self.save_inputs()
  #####################################################################################################
  

#####################################################################################################
# end of "class ControlApp:" ########################################################################
#####################################################################################################










root = tkinter.Tk()
_app = ControlApp(root)
root.mainloop()







