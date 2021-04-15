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
import copy
from Messages.edge_LB import *
from Messages.Messages import *
CACHED_DATA = {"client_edgeserver_test.txt":1}

EDGE_SERVER_INDEX = 0
IP, REQUEST_PORT = constants.EDGE_SERVERS_REQUEST_CREDENTIALS[EDGE_SERVER_INDEX]


request_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
request_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
request_s.bind(('', REQUEST_PORT)) 
request_s.listen(0)

def get_from_origin_servers(filename):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print(colored("SOCKET TO FETCH FROM ORIGIN SERVERS INITIALISED",constants.SUCCESS))
	except:
		print(colored("SOCKET TO FETCH FROM ORIGIN SERVERS COULD NOT BE INITIALISED",constants.FAILURE))
		return

	i = 0
	while(True):
		IP, PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[i%constants.NO_OF_ORIGIN_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			print(colored(f"CONNECTED TO ORIGIN SERVER {IP} AT {PORT}",constants.SUCCESS))
			break
		except:
			print(colored(f"COULD NOT CONNECT TO ORIGIN SERVER {IP} AT {PORT}. RETRYING..",constants.FAILURE))
			time.sleep(1)

	while(True):
		try:
			sock.send(filename.encode())
			content = sock.recv(1024).decode("utf-8")
			if(content == constants.FILE_NOT_FOUND):
				sock.close()
				return False
			else:
				sock.close()
				CACHED_DATA[filename] = content
				return True
		except:
			print(colored(f"COULD NOT SEND DATA! RETRYING.."), constants.FAILURE)

def content_requests_handler():
	while(True):
		request_c, request_addr = request_s.accept()
		name = request_c.recv(1024).decode("utf-8").strip()
		print(colored(f'FILE REQUESTED: {name}', constants.DEBUG))
		if(name in CACHED_DATA.keys()):
			Edge_Server_Client=ResponseContentMessage()
			Edge_Server_Client.filename=name
			Edge_Server_Client.send(request_c)
			#request_c.send(CACHED_DATA[name].encode())
			print(colored(f'CACHED COPY FOUND', constants.DEBUG))
			print(colored(f'FILE SENT', constants.SUCCESS))
		else:
			print(colored("CACHED COPY NOT FOUND. IMPORTING FROM ORIGIN..", constants.DEBUG))
			if(get_from_origin_servers(name)):
				request_c.send(CACHED_DATA[name].encode())
				print(colored("FOUND ON ORIGIN SERVER", constants.DEBUG))
				print(colored(f'FILE SENT', constants.SUCCESS))
			else:
				print(colored("NOT FOUND ON ORIGIN SERVER. TRYING AGAIN.. ", constants.DEBUG))
				time.sleep(10)
				if(get_from_origin_servers(name)):
					request_c.send(CACHED_DATA[name].encode())
					print(colored("FOUND ON ORIGIN SERVER", constants.DEBUG))
					print(colored(f'FILE SENT', constants.SUCCESS))
				else:
					print(colored(f'FILE NOT AVAILABLE', constants.FAILURE))
					request_c.send(constants.FILE_NOT_FOUND.encode())
		request_c.close()

if __name__ == "__main__":
	#send_heartbeat()
	content_requests_handler()