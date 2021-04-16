import sys
sys.path.insert(0, "../")
import socket
import constants
from termcolor import colored
import os.path
class RequestContentMessage(): #between client and edgeserver as well as between edge server and origin server
	
	def __init__(self):
		self.filename = "" #before calling initialise filename	
		self.file_exists=True

	def send(self, soc):
		# edge server ko name send kar raha
		soc.send(self.filename.encode())
		# data = self.filename.read(1024)
		# while data :
		# 	#print("Sending filename from client to edge server")
		# 	soc.send(data)
		# 	data = self.filename.read(1024)
		# #print("Filename sent to edge server")
	
	def receive(self, conn): # send conn wala socket
		# edge server ka reply recieve karo yaha par
		try:
			file_received = open(self.filename+"_receivedcopy", "wb")
			while True:
				#print("Recieving file ....")
				data = conn.recv(1024)
				print(data.decode())
				file_received.write(data)
				if len(data) < 1024 :
					break
			file_received.close()
			print("file received from edge server")
		except:
			self.file_exists=False
		# while True:
		# 	#print("Recieving file ....")
		# 	data = conn.recv(1024)
		# 	file_received.write(data)
		# 	if len(data) < 1024 :
		# 		break
		# file_received.close()
		# print("file received from edge server")


class ResponseContentMessage(): # between edgeserver and client ... to send file
	# if edge server has file then use this message
	# check if edge server has file
	# file is in the directory where the code is running
	def __init__(self):
		self.filename = "" 

	def send(self,soc) :
		file_to_send = open(self.filename, "rb")
		data = file_to_send.read(1024)
		while data:
			#print("Sending file to client")
			soc.send(data)
			data = file_to_send.read(1024)

		file_to_send.close()
		print("file sent to client")

	def receive(self, conn): # This will recieve filename from client
		filename = ""
		data = conn.recv(1024)
		filename += data.decode()
		self.filename = filename 


class FileContentMessage():
	def __init__(self, filename = ""):
		self.filename = filename
		self.exists = False

	def set_name(self, filename):
		self.filename = filename

	def get_name(self):
		return self.filename

	def send_name(self, sock_con):
		sock_con.send(self.filename.encode())

	def receive_name(self, sock_con):
		self.filename = sock_con.recv(1024).decode("utf-8").strip()

	def checkExists(self):
		self.exists = os.path.exists(self.filename)
		return self.exists

	def send_status(self, sock_con):
		if(self.exists):
			sock_con.send(constants.FILE_FOUND.encode())
		else:
			sock_con.send(constants.FILE_NOT_FOUND.encode())

	def receive_status(self, sock_con):
		status = sock_con.recv(1024).decode("utf-8")
		if(status == constants.FILE_FOUND):
			return True
		else:
			return False

	def send_file(self, sock_con):
		file_to_send = open(self.filename, "rb")
		data = file_to_send.read(1024)
		while data:
			print("Sending file to client")
			sock_con.send(data)
			print(data.decode())
			data = file_to_send.read(1024)
		file_to_send.close()
		print(colored("FILE SENT", constants.DEBUG))

	def receive_file(self, sock_con):
		# edge server ka reply recieve karo yaha par
		try:
			file_received = open(self.filename, "wb")
			while True:
				print("Recieving file ....")
				data = sock_con.recv(1024)
				print(data.decode())
				file_received.write(data)
				if len(data) < 1024 :
					break
			file_received.close()
			print(colored("FILE RECEIVED", constants.DEBUG))
			return True
		except:
			return False


class DeleteQueueMessage():
	def __init__(self, DQ = [], DQ_CLOCK = 0):
		self.DQ = DQ
		self.DQ_CLOCK = DQ_CLOCK

	def pack_to_string(array, value):
		result = constants.DELIMITER.join(array)
		result = str(value) + constants.DELIMITER + result
		return result

	def unpack_to_array(result):
		array = result.split(constants.DELIMITER)
		value = int(array[0])
		array = array[1:]
		return (value, array)

	def send(self, sock_con):
		packed_DQ = DeleteQueueMessage.pack_to_string(self.DQ, self.DQ_CLOCK)
		sock_con.send(packed_DQ.encode())

	def receive(self, sock_con):
		packed_DQ = sock_con.recv(1024).decode("utf-8")
		self.DQ_CLOCK, self.DQ = DeleteQueueMessage.unpack_to_array(packed_DQ)


# socket ==> s
# x = RequestContentMessage()
# x.filename = "file1"
# x.send(s)
# x.receive(s)
