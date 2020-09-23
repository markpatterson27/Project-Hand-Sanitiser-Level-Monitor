import machine
import time

charge_pin = machine.Pin(15, machine.Pin.OUT)
read_pin = machine.Pin(13, machine.Pin.IN)

while True:
    charge_pin.on()
    time.sleep(2)
    
    count = 0
    
    charge_pin.off()
    while read_pin.value():
       count = count + 1
        
    print("      ", end='\r')
    print(count, end='\r')
    # print(read_pin.value())
    