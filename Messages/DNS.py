import sys 
sys.path.insert(0, "../")

from constants import *
from struct import *

def stream_ip(ip):
	ip = ip.split('.')
	ip = [int(i).to_bytes(1, 'big') for i in ip]
	return ip

def unstream_ip(ip0, ip1, ip2, ip3):
	return str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))

class DNSreq():
	signature = 'B'+str(MAXLEN_DOMAIN)+'s4cH'
	size = calcsize(signature)

	def __init__(self, add_flag = 1, hostname = "", ip = None, port = None):
		self.add_flag = add_flag
		if len(hostname) > MAXLEN_DOMAIN:
			raise Exception("Length of hostname must be less than 249 characters!")
		self.hostname = hostname
		if add_flag == 0:
			self.ip = ip
			self.port = port
		else:
			self.ip = "0.0.0.0"
			self.port = 0

	def send(self, soc):
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
			self.ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))
			self.port = port

class DNSres():

	"""
	ipblocks - <ip,port> x 2
	"""

	signature = '4cH4cH'
	size = calcsize(signature)

	def __init__(self, ipblocks = None):
		self.ipblocks = ipblocks

	def send(self, soc):
		ip0 = stream_ip(self.ipblocks[0][0])
		ip1 = stream_ip(self.ipblocks[1][0])
		soc.send(pack(DNSres.signature, ip0[0], ip0[1], ip0[2], ip0[3], self.ipblocks[0][1], ip1[0], ip1[1], ip1[2], ip1[3], self.ipblocks[1][1]))

	def receive(self, soc):
		arr = soc.recv(DNSres.size)
		ip00, ip01, ip02, ip03, port0, ip10, ip11, ip12, ip13, port1 = unpack(DNSres.signature, arr)
		self.ipblocks = [(unstream_ip(ip00, ip01, ip02, ip03), port0), (unstream_ip(ip10, ip11, ip12, ip13), port1)]