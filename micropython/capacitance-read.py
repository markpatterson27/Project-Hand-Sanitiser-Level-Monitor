import machine
import time

t = machine.TouchPad(machine.Pin(27))

while True:
    print(t.read(), end='\r')
    time.sleep(1)
