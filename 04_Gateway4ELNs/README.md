# Raspberry Pi as a Gateway

For this task, any RasPi hardware is suitable. No extra hardware or shield is used, but a USB-to-ethernet converter is required for the second network, shown here:

<!---
 <img source="https://github.com/Leibniz-IWT/Raspberry-Pi-FAIRification/blob/main/04_Gateway4ELNs/USB2Ethernet-Adapter.png" alt="USB-to-Ethernet Adapter"  width="200"/>
-->

![USB-to-Ethernet Adapter](https://github.com/Leibniz-IWT/Raspberry-Pi-FAIRification/blob/main/04_Gateway4ELNs/USB2Ethernet-Adapter.png)


For the control of the RasPi, a terminal switch can be used with some cables to connect the RasPi with keyboard, mouse and monitor of the existing computer. These computers are usually operated with an older and now unsupported operating systems, mostly Windows XP or 7.

We have connected the Windows computer with a private network (e.g. 10.0.0.X or 192.168.0.X) using the USB converter to get access to parts of the hard drive. Therefore, disk sharing on the Windows computer must be established before.

The first ethernet port on the RasPi is connected with the internet. Due to the disk sharing option, the files there on the Windows computer can be directly uploaded to the ELN.
