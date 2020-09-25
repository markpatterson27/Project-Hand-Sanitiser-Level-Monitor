# blink function for Lolin D32 LED
import time
from machine import Pin

def blink(pin=5, times = 1, on_seconds = 0.1, off_seconds = 0.1, high_is_on = False):
    led = Pin(pin, Pin.OUT)
    for i in range(times):
        led.on() if high_is_on else led.off()
        time.sleep(on_seconds)
        led.off() if high_is_on else led.on()
        time.sleep(off_seconds)
