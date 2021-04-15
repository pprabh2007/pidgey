import sys
from struct import *

sys.path.insert(0,"../")
from constants import *


class Client_LB_req():

	signature = "HH4c"
	size = calcsize(signature)

	def __init__(self,content_id = None,loc_id = None, prev_edge_ip='0.0.0.0'):
		self.loc_id = loc_id
		self.content_id = content_id
		self.prev_edge_ip = prev_edge_ip

	def send(self,soc):
		loc_id = self.loc_id
		content_id = self.content_id
		prev_edge_ip = self.prev_edge_ip

		# splitting up IP to set as ints
		ip = prev_edge_ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		soc.send(pack(Client_LB_req.signature,content_id,loc_id,ip[0],ip[1],ip[2],ip[3]))

	def receive(self,soc):
		recv_size = 0
		arr = bytearray()
		while recv_size!=Client_LB_req.size:
			temp = soc.recv(Client_LB_req.size-recv_size)
			arr = arr+temp
			recv_size+=len(temp)
			
			if len(arr)<Client_LB_req.size:
				self.received = False
			else:
				self.received = True
				content_id, loc_id, ip0, ip1, ip2, ip3 = unpack(Client_LB_req.signature,arr)
				self.content_id = content_id
				self.loc_id	= loc_id
				self.prev_edge_ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))

class Client_LB_res():

	signature = '4cH'
	size = calcsize(signature)

	def __init__(self, ip = None, port = None):
		self.ip = ip
		self.port = port

	def send(self,soc):
		ip = self.ip
		ip = ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		port = self.port
		soc.send(pack(Client_LB_res.signature,ip[0],ip[1],ip[2],ip[3],port))

	def receive(self,soc):
		arr = soc.recv(Client_LB_res.size)
		if len(arr) < Client_LB_res.size:
			self.received = False
		else:
			self.received = True
			ip0, ip1, ip2, ip3, port = unpack(Client_LB_res.signature,arr)
			self.ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))
			self.port = port