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

DELETE_QUEUE = []
DELETE_QUEUE_CLOCK = 0
SERVER_INDEX = 1
IP, STORE_PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[SERVER_INDEX]
IP, REQUEST_PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[SERVER_INDEX]
IP, DELETE_PORT = constants.ORIGIN_SERVERS_DELETE_CREDENTIALS[SERVER_INDEX]
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

		delete_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		delete_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		delete_s.bind(('', DELETE_PORT)) 
		delete_s.listen(0)

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

				dqm_other = DeleteQueueMessage()
				dqm_other.receive(sync_c)

				dqm_self = DeleteQueueMessage(DELETE_QUEUE, DELETE_QUEUE_CLOCK)
				dqm_self.send(sync_c)

				if(dqm_other.DQ_CLOCK > dqm_self.DQ_CLOCK):
					DELETE_QUEUE = dqm_other.DQ


				curr_files = os.listdir()
				my_files = []
				for file in curr_files:
					if not file.endswith(".py") and file not in DELETE_QUEUE:
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
			while(fcm.filename in DELETE_QUEUE):
				DELETE_QUEUE.remove(fcm.filename)
				DELETE_QUEUE_CLOCK = DELETE_QUEUE_CLOCK + 1
			fcm.receive_file(store_c)
			store_c.close()
			print(colored(f"DATA STORED SUCCESSFULLY!", constants.SUCCESS))
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
			if(fcm.checkExists() and fcm.filename not in DELETE_QUEUE):
				fcm.send_status(request_c)
				fcm.send_file(request_c)
				print(colored(f"REQUESTED FILE DELIVERED SUCCESSFULLY", constants.SUCCESS))
			else:
				fcm.send_status(request_c)
				print(colored(f"REQUESTED FILE NOT FOUND", constants.FAILURE))
			request_c.close()
		except:
			print(colored(f"CONNECTION ERROR. PLEASE TRY AGAIN..", constants.FAILURE))

def delete():
	global DELETE_QUEUE_CLOCK
	fcm = FileContentMessage()
	while(True):
		try:
			delete_c, delete_addr = delete_s.accept()
			fcm.receive_name(delete_c)
			print(colored(f"NAME OF FILE DELETED: {fcm.filename}", constants.SUCCESS))
			DELETE_QUEUE.append(fcm.filename)
			DELETE_QUEUE_CLOCK = DELETE_QUEUE_CLOCK + 1
		except:
			print(colored(f"FILE COULD NOT BE DELETED", constants.FAILURE))


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

	t4 = Thread(target = delete)
	threads.append(t4)
	t4.start()

	for t in threads:
		t.join()
