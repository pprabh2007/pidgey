import sys

sys.path.insert(0, "../")

from constants import *
from struct import *

MSG_DELAY = 5
EDGE_HEARTBEAT_TIME = 1

class Edge_LB():

    signature = 'HQ'
    size = calcsize(signature)

    def __init__(self,loc = 1, load = 0):
        self.loc = loc
        self.load = load

    def send(self, soc):
        soc.send(pack(Edge_LB.signature,self.loc, self.load))

    def receive(self, soc):
        soc.settimeout(MSG_DELAY+5*EDGE_HEARTBEAT_TIME)
        try:
            arr = soc.recv(Edge_LB.size)
            if len(arr) < Edge_LB.size:
                self.received = False
            else:
                self.received = True
                self.loc,self.load = unpack(Edge_LB.signature, arr)
        except Exception as e:
            print(e)
            self.received = False