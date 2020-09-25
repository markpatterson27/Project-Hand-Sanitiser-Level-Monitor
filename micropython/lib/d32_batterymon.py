# script for reading battery voltage levels
from machine import ADC, Pin

# on the Lolin D32, the battery is connected to pin 35.
adc = ADC(Pin(35))

# the battery goes through a 100k/100k potential divider. this will divide the
# the voltages by 2. LiPo batteries can have a voltage up to 4.2V.
# 4.2/2 = 2.1V max input voltage from battery
# attenuate input by 11db gives input measurement range of 3.6V
adc.atten(ADC.ATTN_11DB)

# the ADC are reasonably linear through most of their measurement range. only at
# the top and bottom for their range do they exhibit nonlinearity. in particular,
# it takes an input of about 0.22-0.25V before the ADC start to register an input.
#
# scale_factor and offset determined through measurement and will vary slightly
# between channels and devices, and probably with other factors too.
scale_factor = 0.001604
offset = 0.25

def read_battery():
    return adc.read() * scale_factor + offset

# # calculate battery voltage
# battery_v = adc.read() * scale_factor + offset

# print(battery_v)
