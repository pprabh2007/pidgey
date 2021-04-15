from _thread import *
import socket
import sys
sys.path.insert(0, "../")
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


EDGE_SERVER_INDEX = 0
IP, REQUEST_PORT = constants.EDGE_SERVERS_REQUEST_CREDENTIALS[EDGE_SERVER_INDEX]


request_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
request_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
request_s.bind(('', REQUEST_PORT)) 
request_s.listen(0)

def get_from_origin_servers(filename):
	fcm = FileContentMessage(filename)
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
			fcm.send_name(sock)
			status = fcm.receive_status(sock)
			if(status):
				fcm.receive_file(sock)
				sock.close()
				return True
			else:
				sock.close()
				return False
		except:
			print(colored(f"COULD NOT SEND DATA! RETRYING.."), constants.FAILURE)

def content_requests_handler():
	fcm = FileContentMessage()
	while(True):
		request_c, request_addr = request_s.accept()
		fcm.receive_name(request_c)
		name = fcm.filename
		print(colored(f'FILE REQUESTED: {fcm.filename}', constants.DEBUG))
		if(fcm.checkExists()):
			fcm.send_status(request_c)
			fcm.send_file(request_c)
			#request_c.send(CACHED_DATA[name].encode())
			print(colored(f'CACHED COPY FOUND', constants.DEBUG))
			print(colored(f'FILE SENT', constants.SUCCESS))
		else:
			print(colored("CACHED COPY NOT FOUND. IMPORTING FROM ORIGIN..", constants.DEBUG))
			if(get_from_origin_servers(name)):
				#request_c.send(CACHED_DATA[name].encode())
				fcm.checkExists()
				fcm.send_status(request_c)
				fcm.send_file(request_c)
				print(colored("FOUND ON ORIGIN SERVER", constants.DEBUG))
				print(colored(f'FILE SENT', constants.SUCCESS))
			else:
				print(colored("NOT FOUND ON ORIGIN SERVER. TRYING AGAIN.. ", constants.DEBUG))
				time.sleep(10)
				if(get_from_origin_servers(name)):
					fcm.checkExists()
					fcm.send_status(request_c)
					fcm.send_file(request_c)
					#request_c.send(CACHED_DATA[name].encode())
					print(colored("FOUND ON ORIGIN SERVER", constants.DEBUG))
					print(colored(f'FILE SENT', constants.SUCCESS))
				else:
					fcm.send_status(request_c)
					print(colored(f'FILE NOT AVAILABLE', constants.FAILURE))
		request_c.close()

if __name__ == "__main__":
	#send_heartbeat()
	content_requests_handler()