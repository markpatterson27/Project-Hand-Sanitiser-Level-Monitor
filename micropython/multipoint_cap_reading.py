# program flow
#  - connect to wifi
#  - check if clock set; if not set clock
#  - read capacitances
#  - read battery level
#  - send mqtt message
#  - blink led sucessful/not successful
#  - device sleep

import machine
import utime
import network
import ntptime
import uos
import ubinascii
from umqtt.simple import MQTTClient
import json
import d32_batterymon
import d32_led

import config

# define pins
FULL_PIN = const(13)
TOP_PIN = const(12)
BOTTOM_PIN = const(14)
LED_PIN = config.LED

# setup inputs and outpus
t_full = machine.TouchPad(machine.Pin(FULL_PIN))
t_top = machine.TouchPad(machine.Pin(TOP_PIN))
t_bottom = machine.TouchPad(machine.Pin(BOTTOM_PIN))
led = machine.Pin(LED_PIN, machine.Pin.OUT, value=1)

# MQTT settings
SERVERS = config.MQTT_SERVERS
CLIENT_ID = uos.uname()[0].upper().encode('utf-8') + b"-" + ubinascii.hexlify(machine.unique_id())
BASE_TOPIC = b"hand-sanitiser-levels"
# SUBSCRIBE_TOPIC = BASE_TOPIC + b'/' + CLIENT_ID + b'/messages/#'


# try connecting to access point
def try_connection(nic):
    t = 12
    # console_queue.append(['trying to connect to {}'.format(nic), 10])
    while not nic.isconnected() and t > 0:
        print('.', end='')
        utime.sleep_ms(500)
        t = t - 1
    return nic.isconnected()

# connect to WiFi
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print('connecting to last AP', end='')
    print(try_connection(wlan))
    utime.sleep(2)
    if not wlan.isconnected():
        ## find all APs
        ap_list = wlan.scan()
        ## sort APs by signal strength
        ap_list.sort(key=lambda ap: ap[3], reverse=True)
        ## filter only trusted APs
        ap_list = list(filter(lambda ap: ap[0].decode('UTF-8') in 
                config.ACCESS_POINTS.keys(), ap_list))
        for ap in ap_list:
            if not wlan.isconnected():
                essid = ap[0].decode('UTF-8')
                print('connecting to new AP:', essid, end='')
                wlan.connect(essid, config.ACCESS_POINTS[essid])
                print(try_connection(wlan))
                utime.sleep(2)
            elif wlan.isconnected():
                break
    print('network config: {}'.format(wlan.ifconfig()))

# set rtc
def set_time():
    try:
        ntptime.settime()
    except:
        print('ntp timeout')

# main loop
def run():
    try:
        
        wifi_connect()
        set_time()
        # if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        #     set_time()

        ts = utime.localtime()
        ts = '{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z'.format(
            ts[0], ts[1], ts[2], ts[3], ts[4], ts[5])

        mqtt_payload = {
            'timestamp': ts,
            'meta-data': {
                'device': CLIENT_ID,
                'method': 'multipoint'
            },
            'measures': {
                'capacitance-top': t_top.read(),
                'capacitance-bottom': t_bottom.read(),
                'capacitance-full-length': t_full.read(),
                'battery': d32_batterymon.read_battery()
            }
        }

        for server in SERVERS:
            try:
                server_address_parts = server.split(":")
                print("trying to connect to {}".format(server))
                c = MQTTClient(CLIENT_ID, server_address_parts[0], server_address_parts[1])
                c.connect()
                disconnected = False
            except:
                print("{} not found".format(server))
            else:
                c.publish(BASE_TOPIC + b'/' + CLIENT_ID, json.dumps(mqtt_payload))
                print("MQTT message sent to {}".format(server))
                c.disconnect()
                # c.set_callback(mqtt_cb)
                # c.subscribe(SUBSCRIBE_TOPIC)
                d32_led.blink(LED_PIN, 3, 0.3, 0.3)
                break
        
        # machine.deepsleep(5*60*1000)
            
    except:
        print("something went wrong")
        while _ in range(3):
            d32_led.blink(LED_PIN, 4, 0.1, 0.1)
            utime.sleep(1)
    finally:
        pass
