import sys
sys.path.insert(0, "../")

import socket
from threading import Timer, Thread, Lock
from Messages.edge_LB import *
from Messages.client_LB import *
import time


LOAD_IP = '127.0.0.1'
EDGE_PORT = 6542
CLIENT_PORT = 6543
EDGE_MAX = 100
WEIGHT_DISTANCE = 0.8
WEIGHT_LOAD = 0.2
MAX_CLIENT_REQUESTS= 10

LOCATION = {}
LOCATION[0] = (0.,0.)
LOCATION[1] = (0.,1.)
LOCATION[2] = (1.,0.)
LOCATION[3] = (1.,1.)

# locks and dicts
edge_avail_dict = []
edge_avail_lock  = Lock()
edge_load_dict = {}
edge_load_lock = Lock()

#
def establish_edge():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = LOAD_IP
    port = EDGE_PORT
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))

    sock.listen(EDGE_MAX)

    threads = []

    while(True):
        conn, addr = sock.accept()
        t= Thread(target = recv_edge , args = (conn,addr))
        threads.append(t)
        t.start()
    sock.close()

    for t in threads:
        t.join()

def recv_edge(conn,addr):
    # define edge to Load balancer message
    msg = Edge_LB()
    msg.receive(conn)
    prev_load = -1

    if msg.received:
        print("New edge server connected", addr)
        # prev_load = msg.load
        edge_load_lock.acquire()
        edge_load_dict[addr] = msg.load
        edge_load_lock.release()
        prev_load = msg.load
        edge_avail_lock.acquire()
        edge_avail_dict.append((msg.loc, addr,msg.load))
        edge_avail_lock.release()
    
    while True:
        msg = Edge_LB()
        msg.receive(conn)
        if not msg.received:
            break
        elif prev_load!=msg.load:
            edge_load_lock.acquire()
            edge_load_dict[addr] = msg.load
            edge_load_lock.release()
            prev_load = msg.load
         
        print("Heartbeat received from", addr)

    for e,a in enumerate(edge_avail_dict):
        if a[1] == addr:
            edge_avail_lock.acquire()
            edge_avail_dict.pop(e)
            edge_avail_lock.release()
            edge_load_lock.acquire()
            del edge_load_dict[addr]
            edge_load_lock.release()
            print("connection closed")
            break
    conn.close()

def dist(loc_id1, loc_id2):
	global LOCATION
	print(LOCATION[loc_id1])
	return (LOCATION[loc_id1][0]-LOCATION[loc_id2][0])**2 + (LOCATION[loc_id1][1]-LOCATION[loc_id2][1])**2

def rcv_client(conn,addr):
    msg  = Client_LB_req()
    msg.receive(conn)

    if(msg.received):
        print("Received request: loc id ", msg.loc_id, " from ", addr)

        loc_id = msg.loc_id
        # look in edge_servers_available after acquiring lock
        edge_avail_lock.acquire()
        # At least one edge server would be available
        if(len(edge_avail_dict)==1):
            msg = Client_LB_res(*edge_avail_dict[0][1])
            edge_avail_lock.release()
            msg.send(conn)
            conn.close()
            return

        if(len(edge_avail_dict)==0):
            msg = Client_LB_res('0.0.0.0',EDGE_PORT)
            edge_avail_lock.release()
            msg.send(conn)
            conn.close()
            return

        min_dist = sys.maxsize
        cur_load = sys.maxsize
        best_server_index = 0
        
        for e,server in enumerate(edge_avail_dict):
            
            if server[1]==msg.prev_edge_ip:

                if e == 0:
                    best_server_index = 1
                continue
            
            cur_dist = dist(server[0], loc_id)
            edge_load_lock.acquire()
            
            if WEIGHT_DISTANCE*min_dist+WEIGHT_LOAD*cur_load > WEIGHT_DISTANCE*cur_dist+WEIGHT_LOAD*edge_load_dict[edge_avail_dict[e][1]]:
                min_dist = cur_dist
                cur_load = edge_load_dict[edge_avail_dict[e][1]]
                best_server_index = e
            
            edge_load_lock.release()
        
        

        msg = Client_LB_res(edge_avail_dict[best_server_index][1][0],edge_avail_dict[best_server_index][1][1])
        print(edge_avail_dict[best_server_index][1][1])
        edge_avail_lock.release()
        
        msg.send(conn)

    conn.close()



# Edge server handler thread
t_edge_server_hb = Thread(target = establish_edge)
t_edge_server_hb.start()

# Serve clients
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = LOAD_IP
port = CLIENT_PORT
sock.bind((host,port))
sock.listen(MAX_CLIENT_REQUESTS)

while(True):
    c, addr = sock.accept()
    t = Thread(target = rcv_client,args = (c,addr))
    t.start()

t_edge_server_hb.join()