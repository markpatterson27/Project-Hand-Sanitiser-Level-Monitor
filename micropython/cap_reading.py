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

# define sensor type
METHOD = "multipoint"
# METHOD = "single"

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
SUBSCRIBE_TOPIC = BASE_TOPIC + b'/' + CLIENT_ID + b'/messages/#'

settings = {
    'led_status_blink': True,
    'poll_interval': 5,   # time in minutes
    'polling_hours' : {    # hour of day
        'start': 8,
        'end': 20
    },
    'location': "nowhere"
}

led_blink = False
led_blink_count = 10

# NTP settings
# ntptime.host = config.NTP_SERVER


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
    time_set = False
    for _ in range(2):
        try:
            ntptime.settime()
        except:
            print('ntp timeout')
        else:
            time_set = True
            break
    if not time_set:
        ntptime.host = config.NTP_SERVER
        try:
            ntptime.settime()
        except:
            print('ntp timeout')

# mqtt callback
def mqtt_cb(topic, msg):
    global led_blink, led_blink_count
    global settings

    print("message received")
    print("topic: ", topic)
    print("message: ", msg)

    # led control
    if topic == SUBSCRIBE_TOPIC[:-1]+ b"led":
        if msg == b"on":
            settings['led_status_blink'] = True
        elif msg == b"off":
            settings['led_status_blink'] = False
        elif msg.split(b":")[0] == b"blink":
            led_blink = True
            try:
                if msg.split(b":")[1].isdigit() and int(msg.split(b":")[1]) != 0:
                    led_blink_count = int(msg.split(b":")[1])
                else:
                    led_blink_count = 10
            except IndexError:
                led_blink_count = 10

    # set location
    elif topic == SUBSCRIBE_TOPIC[:-1]+b"location":
        settings['location'] = msg.decode()
        print("location: ", settings['location'])
    
    # change polling interval
    elif topic == SUBSCRIBE_TOPIC[:-1]+b"poll-interval":
        if msg.isdigit():
            settings['poll_interval'] = msg
        print("poll interval: ", settings['poll_interval'])

    # change polling hours
    elif topic == SUBSCRIBE_TOPIC[:-1]+b"polling-hours":
        if msg[0]['start'].isdigit():
            settings['polling_hours']['start'] = msg[0]['start']
        if msg[0]['end'].isdigit():
            settings['polling_hours']['end'] = msg[0]['end']
        print("polling hours: ", settings['polling_hours'])

    machine.RTC().memory(json.dumps(settings))    # save settings to rtc memory


# main loop
def run():
    global led_blink, led_blink_count
    global settings
    
    try:
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            settings = json.loads(machine.RTC().memory()) # load settings from rtc memory
            print('settings retrieved: ', settings)
        else:
            machine.RTC().memory(json.dumps(settings))    # save settings to rtc memory
            print('settings saved: ', settings)
        
        wifi_connect()
        # set_time()
        # if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        #     set_time()

        ts = utime.localtime()
        # if rtc not set, or first poll of polling period
        if ts[0] == 2000 or ts[3] == settings['polling_hours']['start']:
            set_time()
            ts = utime.localtime()

        ts_format = '{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z'.format(
            ts[0], ts[1], ts[2], ts[3], ts[4], ts[5])
        
        c_top = t_top.read()
        c_bottom = t_bottom.read()
        c_full = t_full.read()
        # c_calibrated = c_full / (c_bottom - c_top)

        mqtt_payload = {
            'timestamp': ts_format,
            'meta-data': {
                'device': CLIENT_ID,
                'method': METHOD,
                'location': settings['location']
            },
            'measures': {
                'capacitance-full-length': c_full,
                'battery': d32_batterymon.read_battery()
            }
        }

        if METHOD == "multipoint":
            mqtt_payload['measures']['capacitance-top'] = c_top
            mqtt_payload['measures']['capacitance-bottom'] = c_bottom
            mqtt_payload['measures']['capacitance-calibrated'] = c_full / (c_bottom - c_top)

        for server in SERVERS:
            try:
                server_address_parts = server.split(":")
                print("trying to connect to {}".format(server))
                c = MQTTClient(CLIENT_ID, server_address_parts[0], server_address_parts[1])
                c.connect()
                # disconnected = False
            except:
                print("{} not found".format(server))
            else:
                c.publish(BASE_TOPIC + b'/' + CLIENT_ID + b'/sensor-reading', json.dumps(mqtt_payload))
                print("MQTT message sent to {}".format(server))
                # c.disconnect()
                c.set_callback(mqtt_cb)
                c.subscribe(SUBSCRIBE_TOPIC)
                if settings['led_status_blink']:
                    d32_led.blink(LED_PIN, 3, 0.3, 0.3)
                c.check_msg()
                c.disconnect()
                break

        if led_blink:
            d32_led.blink(LED_PIN, led_blink_count, 0.2, 0.2)
            led_blink = False

        if ts[0] != 2000 and (ts[3] > settings['polling_hours']['end'] or ts[3] < settings['polling_hours']['start']):
            h = (24 - ts[3] + settings['polling_hours']['start'])%24
            m = h*60 - ts[4]
        else:
            m = settings['poll_interval']

        print("deep sleeping for {} minutes".format(m))
        machine.deepsleep(m*60*1000)
            
    except:
        print("something went wrong")
        for _ in range(3):
            d32_led.blink(LED_PIN, 4, 0.1, 0.1)
            utime.sleep(1)
    finally:
        c.disconnect()
