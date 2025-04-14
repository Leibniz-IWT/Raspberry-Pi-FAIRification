# H<sub>2</sub> Measurement Device

A MCC 118 shield is used. Please see [Digilent](https://digilent.com/shop/mcc-118-128-voltage-measurement-daq-hat-for-raspberry-pi/) website for further information. 

The installation procedure is the same as described in [the previous]02_TemperingFurnace](https://github.com/Leibniz-IWT/Raspberry-Pi-FAIRification/tree/main/02_TemperingFurnace).

The MCC 118 shield is used for voltage measurements. Therefore, voltages within the range of specified inputs of +/- 10 V can be directly measured. However, if the signal to be measured is current, then the analog source must be converted with a resistor. Its resistance R is calculated with the Ohm's law:

R = U/I

with the maximum voltage of U = 10 V and the maximum current of the H<sub>2</sub>-Sensor of I = 20 mA. This gives a resistor of R = 500 Ohms. The resistor is mounted in parallel to the input connections of the MCC 118 shield, please see Figure 9 in the paper.
