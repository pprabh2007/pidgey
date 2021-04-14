from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
from termcolor import colored
import selectors
import constants

def request(filename):

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#print("SOCKET CREATED!")
	except:
		print("SOCKET COULD NOT BE CREATED!")
		return

	i = 0
	while(True):
		IP, PORT = constants.EDGE_SERVERS_REQUEST_CREDENTIALS[i%constants.NO_OF_EDGE_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			print(f"CONNECTED TO {IP} AT {PORT}")
			break
		except:
			print(f"COULD NOT CONNECT TO {IP} AT {PORT}, Retrying..")
			time.sleep(1)

	while(True):
		try:
			sock.send(filename.encode())
			content = sock.recv(1024).decode("utf-8")
			print(content)
			sock.close()
			break
		except:
			print("Could not send data! Retrying..")

if __name__ == "__main__":
	while(True):
		name = input()
		request(name)