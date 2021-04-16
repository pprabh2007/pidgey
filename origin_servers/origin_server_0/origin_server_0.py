from _thread import *
import socket
import sys
sys.path.insert(0, "../../")
import os 
import time
import sched
from termcolor import colored
from threading import Timer, Thread
import selectors
import constants
import copy
from Messages.Messages import *

DATA = {'a': "lol"}

SERVER_INDEX = 0
IP, STORE_PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[SERVER_INDEX]
IP, REQUEST_PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[SERVER_INDEX]
#SYNC_PORT = 
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

		print(colored(f"ORIGIN SERVER {SERVER_INDEX} INITIALISED SUCCESSFULLY", constants.SUCCESS))
		break
	except:
		print(colored(f"COULD NOT INITIALISE SERVER {SERVER_INDEX}. RETRYING..", constants.FAILURE))

		

def synchronise():
	while(True):
		IP, PORT = "localhost", constants.SYNC_PORT_2
		try:
			sync_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sync_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sync_s.settimeout(constants.TIMEOUT_PERIOD)
			sync_s.connect((IP, PORT))
			print(colored(f"SYNCING CAPABILITIES WITH {IP} AT {PORT} INITIALISED", constants.SUCCESS))
			while(True):

				curr_files = os.listdir()
				my_files = []
				for file in curr_files:
					if not file.endswith(".py"):
						my_files.append(file)
				n_1 = len(my_files)
				sync_s.send(str(n_1).encode())
				n_2 = int(sync_s.recv(1024).decode())

				fcm = FileContentMessage()
				for filename in my_files:
					fcm.set_name(filename)
					fcm.send_name(sync_s)
					status = fcm.receive_status(sync_s)
					if(status):
						pass
					else:
						fcm.send_file(sync_s)

				fcm = FileContentMessage()
				for i in range(n_2):
					fcm.receive_name(sync_s)
					if(fcm.checkExists()):
						fcm.send_status(sync_s)
					else:
						fcm.send_status(sync_s)
						fcm.receive_file(sync_s)

				print(colored(str(DATA), constants.DEBUG))
				print(colored(f"SYNCED SUCCESSFULLY!", constants.SUCCESS))
				time.sleep(constants.SYNCING_PERIOD)
			sync_s.close()
		except Exception as err:
			print(err)
			print(colored(f"UNABLE TO SYNC WITH {IP} AT {PORT}. RETRYING..", constants.FAILURE))
			try:
				sync_s.close()
			except:
				pass
			time.sleep(1)


	    
def store_content():
	fcm = FileContentMessage()
	while(True):
		try:
			store_c, store_addr = store_s.accept()
			fcm.receive_name(store_c)
			fcm.receive_file(store_c)
			store_c.close()
			print(f"DATA STORED SUCCESSFULLY!")
		except:
			print(colored(f"DATA COULD NOT BE STORED", constants.FAILURE))


def content_requests_handler():
	fcm = FileContentMessage()

	while(True):
		try:
			request_c, request_addr = request_s.accept()
			#print(colored(f"ACCEPTED REQUEST FOR DATA FROM {request_addr}", constants.SUCCESS))
			fcm.receive_name(request_c)
			print(colored(f"NAME OF FILE REQUESTED {fcm.filename}", constants.DEBUG))
			if(fcm.checkExists()):
				fcm.send_status(request_c)
				fcm.send_file(request_c)
				print(colored(f"REQUESTED FILE DELIVERED SUCCESSFULLY", constants.SUCCESS))
			else:
				fcm.send_status(request_c)
				print(colored(f"REQUESTED FILE NOT FOUND", constants.FAILURE))
			request_c.close()
		except:
			print(colored(f"CONNECTION ERROR. PLEASE TRY AGAIN..", constants.FAILURE))



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
