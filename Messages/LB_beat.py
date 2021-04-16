import sys

sys.path.insert(0, "../")

from constants import *
from struct import *

class LB_beat():

	signature = 'B'
	size = calcsize(signature)

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack(LB_beat.signature, 1))

	def receive(self, soc):
		arr = soc.recv(LB_beat.size)
		if len(arr) < LB_beat.size:
			self.received = False
		else:
			self.received = True