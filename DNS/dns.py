#!/usr/bin/env python3

import sys
sys.path.insert(0, "../")
import selectors
import socket
from constants import *
from Messages.DNS import *


sel = selectors.DefaultSelector()

# setting up DNS to listen
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((DNS_IP, DNS_PORT))

sock.listen(DNS_MAX_LISTEN)

hostname_ip = {}

# accept incoming connection
def accept(sock, mask ):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    msg = DNSreq(0)
    msg.receive(conn)
    if not msg.received:
        sel.unregister(conn)
        conn.close()
        return 

    if(msg.add_flag == 0):
        print("adding entry:", msg.hostname, ",", (msg.ip,msg.port))
        if msg.hostname in hostname_ip:
            hostname_ip[msg.hostname].append((msg.ip, msg.port))
        else:
            hostname_ip[msg.hostname] = [(msg.ip, msg.port)]

    # print(hostname_ip)

    # if(vals[0] == '0'):#Add Entry to Table 
    #     hostname_ip[vals[1]] = vals[2]
    #     return conn.sendall(b'IP Added to DNS')
    # else:
    #     print(vals)
    #     if(vals[1]) not in hostname_ip.keys():
    #         return conn.sendall(b"0.0.0.0")
    #     else:
    #         return conn.sendall(bytes(hostname_ip[vals[1]], 'utf-8'))


sel.register(sock, selectors.EVENT_READ, accept)

# for incoming connection
while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        # print(key)
        callback(key.fileobj, mask)


