from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
import selectors
from constants

def send(data):

	try:
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("SOCKET CREATED!")
	except:
		print("SOCKET COULD NOT BE CREATED!")
		return

	i = 0
	while(True):
		IP, PORT = constants.ORIGIN_SERVER_IPS[i%constants.NO_OF_ORIGIN_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			break
		except:
			print(f"COULD NOT CONNECT TO {IP} AT {PORT}")
			print("Retrying.. ")
			time.sleep(10)

	


if __name__ == "__main__":
	send("0")