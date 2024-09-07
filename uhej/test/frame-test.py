#!/usr/bin/env python

import sys
sys.path.append("../")
from uhej import *

def hex(byte_array):
    print("  dump : [" + "".join("%02x " % b for b in byte_array) + "]")

h = hello(32768, "172.16.3.1", "aa:bb:cc:dd:ee:ff", "Testnod")
hex(h)
try:
    d = decode_frame(h)
    print(d)
except IllegalFrameException as e:
    print("Invalid frame '%s'" % h)


q = query(UDP, "tftp")
hex(q)
try:
    d = decode_frame(q)
    print(d)
except IllegalFrameException as e:
    print("Invalid frame '%s'" % q)

services =  [
                {'type':0, 'port':69,   'name':"tftp"},
                {'type':0, 'port':5000, 'name':"test service"}
            ]
s = announce(services)
hex(s)
try:
    d = decode_frame(s)
    print(d)
except IllegalFrameException as e:
    print("Invalid frame '%s'" % s)

