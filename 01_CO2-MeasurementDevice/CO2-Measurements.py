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
import time

import spidev as SPI

#Attention: 'SSD1306.pyc' must be in your working directory:
import SSD1306_python3

import RPi.GPIO as GPIO

import smbus

import busio

import board

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess

import adafruit_pcf8591.pcf8591 as PCF
from adafruit_pcf8591.analog_in import AnalogIn
from adafruit_pcf8591.analog_out import AnalogOut

import numpy as np



###################################################
#Simple calibration using your breath and fresh air
#--------------------------------------------------
#
#see: CO2-MG811-SensorCurve-FitProgram.py

#Replace these values with those from calibration:
U_min=1.3075 #<> 0.042744% CO2 at February, 15th 2025
             #   see: https://www.co2levels.org/
#<> this corresponds to the actually CO2 concentration, see above:
ppm_min=427.44

U_max=0.945 #<> 4% CO2
# <>
ppm_max=40000

#resulting parameters for logarithmic sensor curve:
#(replace with values from calibration:
a=0.11500000000000005
b=1.474236899002716
###################################################




###################################################
#Calculate threshold for alarm activation:
CO2_ppm_Threshold_low= 1500 #ppm
U_Limit_low = -a*np.log10(CO2_ppm_Threshold_low)+b
CO2_ppm_Threshold_high= 2000 #ppm
U_Limit_high = -a*np.log10(CO2_ppm_Threshold_high)+b
""" ... 
Umrechung des Spannungswertes in ppm:
ppm = 10**((b-U)/a)

"""
print("U("+str(ppm_min)+"ppm) = "+str(U_min)+" V")
print("U("+str(ppm_max)+"ppm) = "+str(U_max)+" V")
print("   =>")
print("Equation: U = -"+str(round(a,2))+"*np.log10(ppm)+"+str(round(b,2))+" V/ppm")
print("Lower limit (only LEDs) at "+str(CO2_ppm_Threshold_low)+" ppm")
print("   =>")
print("U_Limit_low = "+str(U_Limit_low)+" V")
print("Upper limit (also with Beeper) at "+str(CO2_ppm_Threshold_high)+" ppm")
print("   =>")
print("U_Limit_high = "+str(U_Limit_high)+" V")
print(" ")
###################################################





###################################################
# Methods for Buzzer
# I2C Adress of I2C Expanders
address = 0x20
def beep_on():
	bus.write_byte(address,0x7F&bus.read_byte(address))
def beep_off():
	bus.write_byte(address,0x80|bus.read_byte(address))

# DISPLAY
# Raspberry Pi pin configuration:
RST = 19
# Note the following are only used with SPI:
DC = 16
bus = 0
device = 0

# 128x64 display with hardware SPI:
disp = SSD1306_python3.SSD1306(RST, DC, SPI.SpiDev(bus,device))
# Initialize library.
disp.begin()
#disp.begin

# Clear display.
disp.clear()
disp.display()
#disp.display

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 1
top = padding
x = padding
# Load default font.
font = ImageFont.load_default()
print('Press Ctrl-C to quit.')


i2c = board.I2C()
pcf = PCF.PCF8591(i2c)
pcf_in_0 = AnalogIn(pcf, PCF.A0)

#Mean value - allocate tmp variable with length 'length_tmp':
length_tmp=1000
tmp=np.empty([length_tmp,1])

#required last command:
bus = smbus.SMBus(1)

# FIRST INFOS ON  DISPLAY:
# 1.Show parameters:
draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top), 'Program parameters:', font=font, fill=255)
draw.text((x, top+20), "Fresh air=421ppm CO2", font=font, fill=255)
draw.text((x, top+40), "<>U_0="+str(U_min)+"V", font=font, fill=255)
disp.image(image)
disp.display()
time.sleep(5)
draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top), '...', font=font, fill=255)
draw.text((x, top+20), "Breath=40000ppm CO2", font=font, fill=255)
draw.text((x, top+40), "<>U_1="+str(U_max)+"V", font=font, fill=255)
disp.image(image)
disp.display()
time.sleep(5)
# 2.choose Buzzer (or not):
draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top),    'Beep? Then:', font=font, fill=255)
draw.text((x, top+20), 'to the left ...', font=font, fill=255)
draw.text((x, top+40), 'if not: down', font=font, fill=255)
disp.image(image)
disp.display()
#Wait for push of Joystick:
KEY = 20 #<> push
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY,GPIO.IN,GPIO.PUD_UP)
value=0xFF
switch=0
while switch == 0:
  bus.write_byte(address,0x0F|bus.read_byte(address))
  value = bus.read_byte(address) | 0xF0
  if value != 0xFF:
    if (value | 0xFE) != 0xFF:
      print("left")
      #WARNING-BEEP ON (=1):
      beepen=1
      switch=1
    elif (value | 0xFB) != 0xFF:
      print("down")
      #WARNING-BEEP OFF (=0):
      beepen=0
      switch=1
  time.sleep(0.01)
# 3.Claim warm-up time.
draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top),    'Warm-up time 5 Min.!', font=font, fill=255)
draw.text((x, top+20), 'Start: Push stick!', font=font, fill=255)
disp.image(image)
disp.display()
#Wait for push of Joystick:
KEY = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY,GPIO.IN,GPIO.PUD_UP)
while GPIO.input(KEY) == 1:
  time.sleep(0.01)


print("Program starts now ...")
draw.text((x, top+40), 'Program starts now!', font=font, fill=255)
disp.image(image)
disp.display()
time.sleep(2)


while True:
  #
  #Delete display:
  #disp.clear()
  # Clear image buffer by drawing a black filled box.
  draw.rectangle((0,0,width,height), outline=0, fill=0)
  #
  # Get measured values:
  for ii in range(0,length_tmp,1):
    tmp[ii]=pcf_in_0.value
  #print(tmp)
  raw_value = np.mean(tmp)
  U_scaled_value = (raw_value / 65535) * pcf_in_0.reference_voltage
  ppm = 10**((b-U_scaled_value)/a)
  # Write two lines of text.
  draw.text((x, top),    'CO2-Konzentration:', font=font, fill=255)
  #Output:
  # ppm:
  tmp_text = "= "+str(round(ppm,1))+" ppm"
  draw.text((x+10, top+20), tmp_text, font=font, fill=255)
  # Volt
  tmp_text = "U = "+str(round(U_scaled_value,4))+" V"
  draw.text((x+10, top+40), tmp_text, font=font, fill=255)
  #
  #Kontrolle auf command line:
  #print("Pin 0: %0.3fV" % (U_scaled_value))
  #
  # Display image.
  disp.image(image)
  disp.display()
  #
  #Warnsignal:
  if U_scaled_value < U_Limit_low: 
    for ii in range(0,3,1):
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      if U_scaled_value < U_Limit_high: 
        if beepen == 1:
          beep_on()
          time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      if U_scaled_value < U_Limit_high: 
        if beepen == 1:
          beep_off()
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      bus.write_byte(address,0xEF);time.sleep(0.1);bus.write_byte(address,0xFF);time.sleep(0.1)
      time.sleep(1)
  else:
    # PAUSE:
    time.sleep(2)
  #
  #disp.clear()
  #disp.display()

