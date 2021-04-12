from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
import selectors
import constants

DATA = {}

SERVER_INDEX = 0
IP, STORE_PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[SERVER_INDEX]
IP, REQUEST_PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[SERVER_INDEX]
#SYNC_PORT = 
store_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
store_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
store_s.bind(('', STORE_PORT)) 
store_s.listen(0)

request_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
request_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
request_s.bind(('', REQUEST_PORT)) 
request_s.listen(0)

def synchronise():
	pass

def store_content():
	while(True):
		store_c, store_addr = store_s.accept()
		print("Accepted store connection from ", store_addr)
		name, content = store_c.recv(1024).decode("utf-8").split("/")
		DATA[name] = content
		store_c.close()
		print("Data Stored!")

def content_requests_handler():
	while(True):
		request_c, request_addr = request_s.accept()
		print("Accepted request from", request_addr)
		name = request_c.recv(1024).decode("utf-8").strip()
		print(name)
		if(name in DATA.keys()):
			request_c.send(DATA[name].encode())
		else:
			request_c.send("Data not found".encode())
		request_c.close()


if __name__ == '__main__':

	threads = []
	
	t1 = Thread(target = store_content)
	threads.append(t1)
	t1.start()
	
	t2 = Thread(target = content_requests_handler)
	threads.append(t2)
	t2.start()

	t3 = Thread(target = synchronise)
	threads.append(t3)
	t3.start()

	for t in threads:
		t.join()
