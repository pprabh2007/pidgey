#!/usr/bin/env python3

import sys
sys.path.insert(0, "../")
import selectors
import socket
from constants import *
from Messages.DNS import *
from threading import Timer, Thread, Lock
from termcolor import colored


sel = selectors.DefaultSelector()

# setting up DNS to listen
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((DNS_IP, DNS_PORT))

sock.listen(DNS_MAX_LISTEN)

# dictionary to store mapping of domain and Ips
hostname_ip = {}

# accept incoming connection
def accept(sock, mask ):
    conn, addr = sock.accept()

    conn.setblocking(False)
    # call read on read on conn
    print(colored("connection acceoted from:" + str(conn), SUCCESS))
    sel.register(conn, selectors.EVENT_READ, read)
    return

def read(conn, mask):
    msg = DNSreq(0)
    msg.receive(conn)
    if not msg.received:
        print(colored("No further message received. Closing connection" ,FAILURE))
        sel.unregister(conn)
        conn.close()
        return 
    # add DNS record
    if(msg.add_flag == 0):
        print("adding entry:", msg.hostname, ",", (msg.ip,msg.port))
        if msg.hostname in hostname_ip:
            hostname_ip[msg.hostname].append((msg.ip, msg.port))
        else:
            hostname_ip[msg.hostname] = [(msg.ip, msg.port)]
        print(colored("DNS Entry successfully added", SUCCESS))
        return
    # else search for record, if not found
    if msg.hostname not in hostname_ip:
        ipblocks=[]
    else:
        # select the first 2 ips
        ipblocks = hostname_ip[msg.hostname][0:2]

    # if number of records is less than 2 , add 0.0.0.0 to it
    while( len(ipblocks) < 2):
        ipblocks.append(('0.0.0.0', 0))

    response = DNSres(ipblocks)
    try:
        response.send(conn)
    except:
        print(colored("Unable to send response to client. Skipping.", FAILURE))
    finally:
        return
    


# on reading on sock, call accept
sel.register(sock, selectors.EVENT_READ, accept)

# threads = []
# for every incoming connection create a thread

# while(True):
#     conn, addr = sock.accept()
#     t= Thread(target = read , args = (conn,addr))
#     threads.append(t)
#     t.start()
# sock.close()

# close the threads
# for t in threads:
#     t.join()

# for incoming connection
while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        # print(key)
        callback(key.fileobj, mask)


