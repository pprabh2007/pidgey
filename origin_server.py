from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
import selectors
import constants

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', 9999)) 
s.listen(5)
c, addr = s.accept()
print("Accepted connection from", addr)

l = c.recv(1024)
print(l)

c.close()
s.close()
