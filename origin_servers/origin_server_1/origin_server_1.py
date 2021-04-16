from _thread import *
import socket
import sys
sys.path.insert(0, "../../")
import os 
import time
import sched
from threading import Timer, Thread
from termcolor import colored
import selectors
import constants
import copy
from Messages.Messages import *

DATA = {'b': "F"}

SERVER_INDEX = 1
IP, STORE_PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[SERVER_INDEX]
IP, REQUEST_PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[SERVER_INDEX]

while(True):
	try:
		store_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		store_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		store_s.bind(('', STORE_PORT)) 
		store_s.listen(0)

		request_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		request_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		request_s.bind(('', REQUEST_PORT)) 
		request_s.listen(0)

		sync_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		sync_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sync_s.bind(('', constants.SYNC_PORT_2)) 
		sync_s.listen(0)
		sync_s.settimeout(constants.TIMEOUT_PERIOD)
		print(colored(f"ORIGIN SERVER {SERVER_INDEX} INITIALISED SUCCESSFULLY", constants.SUCCESS))
		break
	except:
		print(colored(f"COULD NOT INITIALISE SERVER {SERVER_INDEX}. RETRYING..", constants.FAILURE))

def synchronise():
	while(True):
		try:
			sync_c, sync_addr = sync_s.accept()
			sync_c.settimeout(constants.TIMEOUT_PERIOD)
			print(colored(f"SYNCING CAPABILITIES WITH {sync_addr} INITIALISED", constants.SUCCESS))
			while(True):

				curr_files = os.listdir()
				my_files = []
				for file in curr_files:
					if not file.endswith(".py"):
						my_files.append(file)

				print(my_files)

				n_1 = int(sync_c.recv(1024).decode("utf-8"))
				n_2 = len(my_files)
				sync_c.send(str(n_2).encode())

				for i in range(n_1):
					fcm = FileContentMessage()
					fcm.receive_name(sync_c)
					if(fcm.checkExists()):
						fcm.send_status(sync_c)
					else:
						fcm.send_status(sync_c)
						fcm.receive_file(sync_c)
					time.sleep(1)

				
				for filename in my_files:
					fcm = FileContentMessage(filename)
					fcm.send_name(sync_c)
					status = fcm.receive_status(sync_c)
					if(status):
						pass
					else:
						fcm.send_file(sync_c)
					time.sleep(1)

				print(colored(f"SYNCED SUCCESSFULLY!", constants.SUCCESS))
						
		except Exception as err:
			print(err)
			print(colored(f"UNABLE TO SYNC ", constants.FAILURE))

     


def store_content():
	fcm = FileContentMessage()
	while(True):
		try:
			store_c, store_addr = store_s.accept()
			fcm.receive_name(store_c)
			fcm.receive_file(store_c)
			store_c.close()
			print(colored(f"DATA STORED SUCCESSFULLY!", constants.SUCCESS))
		except:
			print(colored(f"DATA COULD NOT BE STORED", constants.FAILURE))


def content_requests_handler():
	while(True):
		try:
			request_c, request_addr = request_s.accept()
			#print(colored(f"ACCEPTED REQUEST FOR DATA FROM {request_addr}", constants.SUCCESS))
			name = request_c.recv(1024).decode("utf-8").strip()
			print(colored(f"NAME OF FILE REQUESTED {name}", constants.DEBUG))
			if(name in DATA.keys()):
				request_c.send(DATA[name].encode())
				print(colored(f"REQUESTED FILE DELIVERED SUCCESSFULLY", constants.SUCCESS))
			else:
				request_c.send(constants.FILE_NOT_FOUND.encode())
				print(colored(f"REQUESTED FILE NOT FOUND", constants.FAILURE))
			request_c.close()
		except:
			print(colored(f"CONNECTION ERROR. PLEASE TRY AGAIN.. ", constants.FAILURE))

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
