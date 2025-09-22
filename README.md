# Raspberry-Pi FAIRification Projects

### Programs for Measurements and Data Applications

The background of this repo is the usage of hardware, for instance legacy devices, runnin old controller or computer with outdated operating system that lacks a secure internet connection. These devices are still fully usable, but their data cannot be upploaded because of the missing internet connection.

To resolve this kind of problems, four different applications are described based on a Raspberry Pi (RasPi) single board computer as a fast and cheap solution to enable a FAIR (Findable, Accessible, Interoperable, Reusable) data management. All RasPis are running a Raspian operating system, but they differ in the additionally installed software, depending on the used hardware.

It starts with a CO<sub>2</sub> standalone measurement device as a general example for the development of an entire internet accessible measurement system.

The second application is suitable for older legacy devices which lack internet connections. In this case, a tempering furnace is equiped with a Raspberry Pi, an interface shield and a TFT touchpad as a user interface.

A different touchpad is used for the third example, mounted in an own box, with a similar configuration as in the second case. 

The last example is the most simple one. It requires only a USB-ethernet converter to connect to vulnerable measurement and process computers with outdated operating systems. Then, data from these computers can be directly  uploaded to electronic laboratory notebooks or other data management system.

All these applications are explained in more detail in the paper [FAIRification of Legacy Devices and Measurement Applications with Single Board Computers](https://link.springer.com/article/10.1007/s40192-025-00398-2) and promoted by the journal editor Taylor Sparks in [this video](https://www.youtube.com/watch?v=LsobJSKk37I).