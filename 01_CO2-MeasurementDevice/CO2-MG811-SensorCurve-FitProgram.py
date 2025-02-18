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
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import fsolve





#####################################################################
# 1. Setpoint: Environment
#
# Keep device for at least five minutes on fresh air (opened window);
# then read voltage on the display and paste it here (say "1.3075"):
U_min=1.3075 #<> 0.042744% CO2 at February, 15th 2025
             #   see: https://www.co2levels.org/
#<> this corresponds to the actually CO2 concentration, see above:
ppm_min=427.44
#####################################################################





#####################################################################
# 2. Setpoint: Respiratory air
#
# Our breath, i.e. the air from our lungs, show a remarkable
# constant CO2 concentration of 4% if you are rested and relaxed;
# take the device in a bag and flood its interior by exhaling 
# with your mouth while inhaling via nose and paste that voltage
# (say "1.0505"):
U_max=1.0505 #<> 4% CO2 -> Geraet 2
# <>
ppm_max=40000
#####################################################################





#####################################################################
# FITTING

#Function from: Shen, An investigation of a low-cost CO 2 indoor 
#               air quality monitor (2014)
c=U_min-np.log(ppm_min)
b=(np.exp(c)*np.exp(U_max)-ppm_min)/(ppm_max-ppm_min)

#initial guess:
a_0=0.5
b_0=-6

def equations(p):
    a, b = p
    return (-a*np.log10(ppm_min)+b-U_min, -a*np.log10(ppm_max)+b-U_max)

a, b =  fsolve(equations, (a_0, b_0))


print("----------------------------")
print("LOGARITHMIC APPROACH")
print("Ansatz: U = -ln(a*ppm)+b")
print("a = "+str(a)+", b = "+str(b))
#CHECK:
#give a test voltage, e.g.
U_test=1.1
#=>
ppm_test=10**((b-U_test)/a)

print("U_test = "+str(U_test)+" V")
print("   =>")
print("ppm = "+str(ppm_test)+" ppm")
print("----------------------------")
print(" ")
#####################################################################
























