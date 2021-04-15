import sys
import socket
sys.path.insert(0, "../")

class RequestContentMessage(): #between client and edgeserver
	
	def __init__(self):
		self.filename = "" #before calling initialise filename	

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
		file_received = open(self.filename, "wb")
		while True:
			#print("Recieving file ....")
			data = conn.recv(1024)
			file_received.write(data)
			if len(data) < 1024 :
				break
		file_received.close()
		print("file received from edge server")


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

socket ==> s
x = RequestContentMessage()
x.filename = "file1"
x.send(s)
x.receive(s)
