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

DELETE_QUEUE = []
DELETE_QUEUE_CLOCK = 0
SERVER_INDEX = 0
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

		delete_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		delete_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		delete_s.bind(('', DELETE_PORT)) 
		delete_s.listen(0)

		print(colored(f"ORIGIN SERVER {SERVER_INDEX} INITIALISED SUCCESSFULLY", constants.SUCCESS))
		break
	except:
		print(colored(f"COULD NOT INITIALISE SERVER {SERVER_INDEX}. RETRYING..", constants.FAILURE))

		
def synchronise():
	global DELETE_QUEUE_CLOCK
	global DELETE_QUEUE
	while(True):
		IP, PORT = "localhost", constants.SYNC_PORT_2
		try:
			sync_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sync_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sync_s.settimeout(constants.TIMEOUT_PERIOD)
			sync_s.connect((IP, PORT))
			print(colored(f"SYNCING CAPABILITIES WITH {IP} AT {PORT} INITIALISED", constants.SUCCESS))
			while(True):


				dqm_self = DeleteQueueMessage(DELETE_QUEUE, DELETE_QUEUE_CLOCK)
				dqm_self.send_q(sync_s)

				dqm_other = DeleteQueueMessage()
				dqm_other.receive_q(sync_s)

				if(dqm_other.DQ_CLOCK > dqm_self.DQ_CLOCK):
					DELETE_QUEUE = copy.deepcopy(dqm_other.DQ)
				
				time.sleep(1)

				curr_files = os.listdir()
				my_files = []
				for file in curr_files:
					if not file.endswith(".py") and file not in DELETE_QUEUE:
						my_files.append(file)

				print(my_files)

				n_1 = len(my_files)
				sync_s.send(str(n_1).encode())
				n_2 = int(sync_s.recv(1024).decode())

				for filename in my_files:
					fcm = FileContentMessage(filename)
					fcm.send_name(sync_s)
					status = fcm.receive_status(sync_s)
					if(status):
						pass
					else:
						fcm.send_file(sync_s)
					time.sleep(1)

				for i in range(n_2):
					fcm = FileContentMessage()
					fcm.receive_name(sync_s)
					if(fcm.checkExists()):
						fcm.send_status(sync_s)
					else:
						fcm.send_status(sync_s)
						fcm.receive_file(sync_s)
					time.sleep(1)

				print(colored(f"SYNCED SUCCESSFULLY!", constants.SUCCESS))
				time.sleep(constants.SYNCING_PERIOD)
			sync_s.close()
		except Exception as e:
			print(e)
			print(colored(f"UNABLE TO SYNC WITH {IP} AT {PORT}. RETRYING..", constants.FAILURE))
			try:
				sync_s.close()
			except:
				pass
			time.sleep(constants.SYNCING_PERIOD/8)


	    
def store_content():
	global DELETE_QUEUE_CLOCK
	global DELETE_QUEUE
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
			print(f"DATA STORED SUCCESSFULLY!")
		except Exception as e:
			print(e)
			print(colored(f"DATA COULD NOT BE STORED", constants.FAILURE))


def content_requests_handler():
	global DELETE_QUEUE_CLOCK
	global DELETE_QUEUE
	fcm = FileContentMessage()

	while(True):
		try:
			request_c, request_addr = request_s.accept()
			#print(colored(f"ACCEPTED REQUEST FOR DATA FROM {request_addr}", constants.SUCCESS))
			fcm.receive_name(request_c)
			print(colored(f"NAME OF FILE REQUESTED {fcm.filename}", constants.DEBUG))
			if(fcm.checkExists(DELETE_QUEUE) ):
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
	global DELETE_QUEUE
	fcm = FileContentMessage()
	while(True):
		try:
			delete_c, delete_addr = delete_s.accept()
			fcm.receive_name(delete_c)
			print(colored(f"NAME OF FILE DELETED: {fcm.filename}", constants.SUCCESS))
			DELETE_QUEUE.append(fcm.filename)
			DELETE_QUEUE_CLOCK = DELETE_QUEUE_CLOCK + 1
		except Exception as e:
			print(e)
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
