#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 6542        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect((HOST, PORT))

# while True:
s.sendall(b'0 www.chutiyahotum.com 1.2.3.4')
data = s.recv(1024)
print(repr(data))

# print('Received', repr(data))
