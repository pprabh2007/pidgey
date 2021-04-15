import sys 
sys.path.insert(0, "../")

from constants import *
from struct import *


# class for sending and accepting an object of DNSreq
class DNSreq():
	signature = 'B'+str(MAXLEN_DOMAIN)+'s4cH'
	size = calcsize(signature)

	def __init__(self, add_flag = 1, hostname = "", ip = "0.0.0.0", port = 0):
		self.add_flag = add_flag
		if len(hostname) > MAXLEN_DOMAIN:
			raise Exception("Length of hostname must be less than 249 characters!")
		self.hostname = hostname
		self.ip = ip
		self.port = port

	def send(self, soc):
		# splitting up ip to send as ints
		ip = self.ip
		ip = ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		soc.send(pack(DNSreq.signature, self.add_flag, self.hostname.encode(), ip[0], ip[1], ip[2], ip[3], self.port))

	def receive(self, soc):
		arr = soc.recv(DNSreq.size)
		if len(arr) < DNSreq.size:
			self.received = False
		else:
			self.received = True
			add_flag, hostname, ip0, ip1, ip2, ip3, port = unpack(DNSreq.signature, arr)
			self.add_flag = add_flag
			self.hostname = hostname.decode().strip()
			# re assembling IP
			self.ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))
			self.port = port

# class for sending and accepting an object of DNSres
class DNSres():

	signature = '4cH4cH'
	size = calcsize(signature)

	def __init__(self, ipblocks = None):
		self.ipblocks = ipblocks

	def send(self, soc):
		ip0 = self.ipblocks[0][0]
		ip0 = ip0.split('.')
		ip0 = [int(i).to_bytes(1, 'big') for i in ip0]

		ip1 = self.ipblocks[1][0]
		ip1 = ip1.split('.')
		ip1 = [int(i).to_bytes(1, 'big') for i in ip1]


		soc.send(pack(DNSres.signature, ip0[0], ip0[1], ip0[2], ip0[3], self.ipblocks[0][1], ip1[0], ip1[1], ip1[2], ip1[3], self.ipblocks[1][1]))

	def receive(self, soc):
		arr = soc.recv(DNSres.size)
		ip00, ip01, ip02, ip03, port0, ip10, ip11, ip12, ip13, port1 = unpack(DNSres.signature, arr)
		
		block1 = str(int.from_bytes(ip00, 'big')) + "." + str(int.from_bytes(ip01, 'big')) + "." + str(int.from_bytes(ip02, 'big')) + "." + str(int.from_bytes(ip03, 'big'))
		block2 = str(int.from_bytes(ip10, 'big')) + "." + str(int.from_bytes(ip11, 'big')) + "." + str(int.from_bytes(ip12, 'big')) + "." + str(int.from_bytes(ip13, 'big'))
		
		self.ipblocks = [(block1, port0), (block2, port1)]