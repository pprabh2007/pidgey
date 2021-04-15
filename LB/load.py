import sys
sys.path.insert(0, "../")

import socket
from threading import Timer, Thread, Lock
from Messages.edge_LB import *
from Messages.client_LB import *
from Messages.DNS import *
import time
from constants import *
from termcolor import colored

# locks and dicts
edge_avail_dict = []
edge_avail_lock  = Lock()
edge_load_dict = {}
edge_load_lock = Lock()

# Handles incoming connections from edge server
def establish_edge():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LOAD_IP, EDGE_PORT))
    sock.listen(EDGE_MAX)

    threads = []

    # for every incoming connection create a thread that is handles by rcv edge
    while(True):
        conn, addr = sock.accept()
        t= Thread(target = recv_edge , args = (conn,addr))
        threads.append(t)
        t.start()
    sock.close()

    # close the threads
    for t in threads:
        t.join()

# edge server message handler
def recv_edge(conn,addr):
    # define edge to Load balancer message
    msg = Edge_LB()
    msg.receive(conn)
    prev_load = -1

    # initial message handler
    if (msg.received):
        # atomically add the load of edge server to dict
        edge_load_lock.acquire()
        edge_load_dict[addr] = msg.load
        edge_load_lock.release()
        
        # prev load keeps track of last known load of the edge server
        prev_load = msg.load

        # atomically add edge server to list of availible edge severs
        edge_avail_lock.acquire()
        edge_avail_dict.append((msg.loc, addr,msg.load))
        edge_avail_lock.release()

        print(colored("New edge server connected : " + str(addr),SUCCESS))
    
    # for every consequtive message received
    while True:
        msg = Edge_LB()
        msg.receive(conn)
        if not msg.received:
            print(colored("Edge server closed connection from : " + str(addr),FAILURE))
            break
        # if load has changed
        elif prev_load!=msg.load:
            # atomically update load
            edge_load_lock.acquire()
            edge_load_dict[addr] = msg.load
            edge_load_lock.release()
            prev_load = msg.load
         
        print("Message(heartbeat) received from edge server - ", addr)

    # if message is not received
    # search for the edge server
    for e,a in enumerate(edge_avail_dict):
        if a[1] == addr:
            # atomically pop it from the dict
            edge_avail_lock.acquire()
            edge_avail_dict.pop(e)
            edge_avail_lock.release()
            # remove corresponding load
            edge_load_lock.acquire()
            del edge_load_dict[addr]
            edge_load_lock.release()
            print("Removed following edge edge server from availible list - ", addr)
            break
    # close the connection
    conn.close()

# gets the dist between two local Ids
def dist(loc_id1, loc_id2):
	return (LOCATION[loc_id1][0]-LOCATION[loc_id2][0])**2 + (LOCATION[loc_id1][1]-LOCATION[loc_id2][1])**2

# handles request from clients
def rcv_client(conn,addr):
    msg  = Client_LB_req()
    msg.receive(conn)

    if(msg.received):
        print("Received request from client: loc id ", msg.loc_id, " from ", addr)

        loc_id = msg.loc_id
        # look in edge_servers_available after acquiring lock
        edge_avail_lock.acquire()
        # search for availaible edge servers

        # no edge servers availaible
        if(len(edge_avail_dict)==0):
            msg = Client_LB_res('0.0.0.0', 0)
            edge_avail_lock.release()
            msg.send(conn)
            conn.close()
            return
        # only 1 edge server avalaible
        elif(len(edge_avail_dict)==1):
            msg = Client_LB_res(*edge_avail_dict[0][1])
            edge_avail_lock.release()
            msg.send(conn)
            conn.close()
            return

        min_dist = sys.maxsize
        cur_load = sys.maxsize
        best_server_index = 0
        
        # find the best edge sever
        for e,server in enumerate(edge_avail_dict):
            # if prev edge server is availible, assign it
            if server[1]==msg.prev_edge_ip:
                # ???
                if e == 0:
                    best_server_index = 1
                continue
            # calculate dist from selected edge server
            cur_dist = dist(server[0], loc_id)
            
            edge_load_lock.acquire()
            # check if weightage of load and dist is less than prev
            if WEIGHT_DISTANCE*min_dist+WEIGHT_LOAD*cur_load > WEIGHT_DISTANCE*cur_dist+WEIGHT_LOAD*edge_load_dict[edge_avail_dict[e][1]]:
                min_dist = cur_dist
                cur_load = edge_load_dict[edge_avail_dict[e][1]]
                best_server_index = e
            edge_load_lock.release()
        
        # send best availaible edge server
        msg = Client_LB_res(edge_avail_dict[best_server_index][1][0],edge_avail_dict[best_server_index][1][1])
        edge_avail_lock.release()
        
        try:
            msg.send(conn)
        except:
            print(colored("connection by client has already been closed, edge server IP not sent",FAILURE))
            return

    conn.close()



# Edge server handler thread
t_edge_handler = Thread(target = establish_edge)
t_edge_handler.start()

# Register itself to DNS
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
s.connect((DNS_IP, DNS_PORT))

print("Registering load balancer IP to DNS")
msg = DNSreq(0, LB_DOMAIN, LOAD_IP, CLIENT_PORT)
msg.send(s)
s.close()

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

t_edge_handler.join()