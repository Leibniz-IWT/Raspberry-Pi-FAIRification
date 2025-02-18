# Reading Recorder for a Tempering Furnace

## Thermocouple Shield for the Raspberry Pi


https://digilent.com/shop/mcc-134-thermocouple-measurement-daq-hat-for-raspberry-pi/

Download Python library:
https://github.com/mccdaq/daqhats

ATTENTION: Shield is only for thermocouples, not for thermistors like PT100


Installation of drivers:
https://github.com/mccdaq/daqhats
-> download + 'install.sh'



## Installation of MCC-134-Boards

see:
https://www.mccdaq.com/DAQ-HAT/MCC-134.aspx
https://github.com/mccdaq/daqhats
https://mccdaq.github.io/daqhats/install.html


-> as sudo:  
apt update  
apt full-upgrade  
apt install git  

->as User:  
git clone https://github.com/mccdaq/daqhats.git

-> again as sudo:  
cd daqhats/  
./install.sh

-> further required drivers:  
apt install python3-pip  
apt install python3-plotly python3-pandas  
pip3 install dash  


-> check installation:  

- connect a standard thermocouple (e.g. from a digital multimeter) to CH0 H and CH0 L
- as User:   
  cd ~/daqhats/examples/python/mcc134/web_server
  then:  
  python3 web_server.py
- Open browser and enterthis link:  
  http://[IP address of RaspPi]:8080  
- configure 'Channel 0' as 'K-Typ' auswählen  
- start


=> measurement values
___________________________________________________________________________



















