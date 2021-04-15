#!/usr/bin/env python3
import sys
sys.path.insert(0, "../")
import socket
from constants import *
from Messages.DNS import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect((DNS_IP, DNS_PORT))

# while True:
msg = DNSreq(1,"www.tuchutiya.com")
while(True):
    msg.send(s)

    msg1 = DNSres()

    msg1.receive(s)

    print(msg1.ipblocks)