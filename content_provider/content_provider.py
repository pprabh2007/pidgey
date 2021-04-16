from _thread import *
import socket
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "../")
import os 
import time
import sched
from threading import Timer, Thread
from termcolor import colored
import selectors
import constants
from Messages.Messages import *


def send(filename):
	fcm = FileContentMessage(filename)
	if(not fcm.checkExists()):
		print(colored("FILE NOT FOUND", constants.FAILURE))
		return

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print(colored("CONTENT PROVIDER INITIALISED", constants.SUCCESS))
	except:
		print(colored("UNABLE TO INITIALISE CONTENT PROVIDER", constants.FAILURE))
		return

	i = 0
	while(True):
		IP, PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[i%constants.NO_OF_ORIGIN_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			print(colored(f"CONNECTED TO {IP} AT {PORT}", constants.SUCCESS))
			break
		except:
			print(colored(f"COULD NOT CONNECT TO {IP} AT {PORT}. RETRYING.. ", constants.FAILURE))
			time.sleep(1)

	while(True):
		try:
			fcm.send_name(sock)
			time.sleep(1)
			fcm.send_file(sock)
			sock.close()
			print(colored(f"DATA SENT SUCCESSFULLY", constants.SUCCESS))
			break
		except:
			print(colored("COULD NOT SEND DATA. RETRYING.. ", constants.FAILURE))

def delete(filename):
	fcm = FileContentMessage(filename)
	if(not fcm.checkExists()):
		print(colored("FILE NOT FOUND", constants.FAILURE))
		return

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print(colored("CONTENT DELETER INITIALISED", constants.SUCCESS))
	except:
		print(colored("UNABLE TO INITIALISE CONTENT DELETER", constants.FAILURE))
		return

	i = 0
	while(True):
		IP, PORT = constants.ORIGIN_SERVERS_DELETE_CREDENTIALS[i%constants.NO_OF_ORIGIN_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			print(colored(f"CONNECTED TO {IP} AT {PORT}", constants.SUCCESS))
			break
		except:
			print(colored(f"COULD NOT CONNECT TO {IP} AT {PORT}. RETRYING.. ", constants.FAILURE))
			time.sleep(1)

	while(True):
		try:
			fcm.send_name(sock)
			sock.close()
			print(colored(f"FILENAME SENT SUCCESSFULLY", constants.SUCCESS))
			break
		except:
			print(colored("COULD NOT SEND FILENAME. RETRYING.. ", constants.FAILURE))

if __name__ == "__main__":
	while(True):
		action = input()
		filename = input()
		if(action.upper() == "ADD"):
			send(filename)
		else:
			delete(filename)