import unittest
import os, sys

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

# import file to test
import cap_reading


class Test_CapReadingMQTTCb(unittest.TestCase):
    '''
    '''

    def setUp(self):
        '''
        '''
        pass

    def test_passing(self):
        '''
        '''
        self.assertTrue(True)