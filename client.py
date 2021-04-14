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
	while(True):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			print(colored("CLIENT INITIALISED", constants.SUCCESS))
			break
		except:
			print(colored("COULD NOT INITIALISE CLIENT. RETRYING", constants.FAILURE))
			
	i = 0
	while(True):
		IP, PORT = constants.EDGE_SERVERS_REQUEST_CREDENTIALS[i%constants.NO_OF_EDGE_SERVERS]	
		i = i + 1
		try:
			sock.connect((IP, PORT))
			print(colored(f"CONNECTED TO {IP} AT {PORT}", constants.SUCCESS))
			break
		except:
			print(colored(f"COULD NOT CONNECT TO {IP} AT {PORT}. RETRYING..", constants.FAILURE))
			time.sleep(1)

	while(True):
		try:
			sock.send(filename.encode())
			content = sock.recv(1024).decode("utf-8")
			if(content == constants.FILE_NOT_FOUND):
				print(colored(f"FILE {filename} NOT FOUND", constants.FAILURE))
			else:
				print(colored(f"CONTENTS OF FILE {filename} ARE:", constants.SUCCESS))
				print(content)
			sock.close()
			break
		except:
			print(colored(f"UNABLE TO FETCH. RETRYING..", constants.FAILURE))

if __name__ == "__main__":
	while(True):
		name = input()
		request(name)