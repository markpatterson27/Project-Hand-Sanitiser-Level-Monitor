import unittest
import os, sys
import json

# add module dirs to path
# sys.path.append("../")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..' , 'micropython'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'micropython', 'lib'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stubs'))

# map python modules to micropython names
import binascii, os, socket, struct, time

sys.modules['ubinascii'] = binascii
# sys.modules['uos'] = os
sys.modules['usocket'] = socket
sys.modules['ustruct'] = struct
sys.modules['utime'] = time

import _config
sys.modules['config'] = _config

# import file to test
import cap_reading


class Test_CapReadingMQTTCb(unittest.TestCase):
    ''' test mqtt_cb callback function
    '''

    def setUp(self):
        '''
        '''
        # set initial settings
        cap_reading.led_blink = False
        cap_reading.led_blink_count = 10
        cap_reading.settings = {
            'led_status_blink': True,
            'poll_interval': 5,   # time in minutes
            'polling_hours' : {    # hour of day
                'start': 8,
                'end': 20
            },
            'location': "nowhere"
        }

    def test_led_control(self):
        '''
        test led control messages are parsed

        states checked:
          - on -> on
          - on -> off
          - off -> on
          - off -> off
          - nonsense message -> no state change
        '''
        topic = cap_reading.SUBSCRIBE_TOPIC[:-1] + b"led"

        cap_reading.led_blink = False
        cap_reading.led_blink_count = 10

        # test status led on/off
        start_values = [True, False]
        for start_value in start_values:
            with self.subTest('on'):
                cap_reading.settings['led_status_blink'] = start_value
                message = b"on"

                cap_reading.mqtt_cb(topic, message)

                self.assertTrue(cap_reading.settings['led_status_blink'])
                self.assertFalse(cap_reading.led_blink)

            with self.subTest('off'):
                cap_reading.settings['led_status_blink'] = start_value
                message = b"off"

                cap_reading.mqtt_cb(topic, message)

                self.assertFalse(cap_reading.settings['led_status_blink'])
                self.assertFalse(cap_reading.led_blink)

            with self.subTest('nonsense'):
                cap_reading.settings['led_status_blink'] = start_value
                message = b"nonsense"

                cap_reading.mqtt_cb(topic, message)

                self.assertEqual(cap_reading.settings['led_status_blink'], start_value)
                self.assertFalse(cap_reading.led_blink)

        # test blink parsing
        messages = [b"blink", b"blink:nonsense", b"blink:5.3"]
        for message in messages:
            with self.subTest(message):
                cap_reading.led_blink = False
                cap_reading.led_blink_count = 10
                # message = b"blink"
                cap_reading.mqtt_cb(topic, message)
                self.assertTrue(cap_reading.led_blink)
                self.assertEqual(cap_reading.led_blink_count, 10)
                self.assertFalse(cap_reading.settings['led_status_blink'])
        for i in range(1, 21):
            with self.subTest('blink:'+str(i)):
                cap_reading.led_blink = False
                cap_reading.led_blink_count = 10
                message = b"blink:" + str(i).encode()
                cap_reading.mqtt_cb(topic, message)
                self.assertTrue(cap_reading.led_blink)
                self.assertEqual(cap_reading.led_blink_count, i)
                self.assertFalse(cap_reading.settings['led_status_blink'])

    def test_location_setting(self):
        '''
        test location messages set location
        '''
        topic = cap_reading.SUBSCRIBE_TOPIC[:-1] + b"location"

        locations = ['somewhere', 'not here', 'over there', '123456']

        for location in locations:
            cap_reading.settings['location'] = 'nowhere'    # reset location
            message = location.encode()
            cap_reading.mqtt_cb(topic, message)
            with self.subTest(location):
                self.assertEqual(cap_reading.settings['location'], location)

    def test_pollinterval_setting(self):
        '''
        test poll-interval messages set the polling interval
        '''
        topic = cap_reading.SUBSCRIBE_TOPIC[:-1] + b"poll-interval"

        # test int intervals
        for i in range(1, 60):
            cap_reading.settings['poll_interval'] = 5    # reset interval
            cap_reading.mqtt_cb(topic, i)
            with self.subTest(i):
                self.assertEqual(cap_reading.settings['poll_interval'], i)

        # test not intervals
        intervals = ['nan', b'nonsense', 4.4, 4.8, 5.3, 7.8]
        for interval in intervals:
            cap_reading.settings['poll_interval'] = 5    # reset interval
            cap_reading.mqtt_cb(topic, interval)
            with self.subTest(interval):
                self.assertEqual(cap_reading.settings['poll_interval'], 5)

    def test_pollinghours_setting(self):
        '''
        test polling-hours messages set the polling hours
        '''
        topic = cap_reading.SUBSCRIBE_TOPIC[:-1] + b"polling-hours"

        cap_reading.settings['polling_hours'] = {    # hour of day
            'start': 8,
            'end': 20
        }

        # test changing one key at a time
        for k in cap_reading.settings['polling_hours'].keys():
            for i in range(0,24):
                cap_reading.settings['polling_hours'] = {    # reset
                    'start': 8,
                    'end': 20
                }
                message = {k: i}
                cap_reading.mqtt_cb(topic, json.dumps(message))
                with self.subTest(k+str(i)):
                    self.assertEqual(cap_reading.settings['polling_hours'][k], i)

        # test changing both keys at a time
        for i in range(0,24):
            for j in range(0,24):
                cap_reading.settings['polling_hours'] = {    # reset
                    'start': 8,
                    'end': 20
                }
                message = {
                    'start': i,
                    'end': j
                }
                cap_reading.mqtt_cb(topic, json.dumps(message))
                with self.subTest(str(i)+':'+str(j)):
                    self.assertEqual(cap_reading.settings['polling_hours']['start'], i)
                    self.assertEqual(cap_reading.settings['polling_hours']['end'], j)

