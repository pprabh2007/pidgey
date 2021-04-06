#!/usr/bin/env python3

import sys
import selectors
import socket
DNS_IP = '127.0.0.1'
DNS_PORT = 6542
DNS_MAX_LISTEN = 100


sel = selectors.DefaultSelector()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = DNS_IP
port = DNS_PORT

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))

sock.listen(DNS_MAX_LISTEN)

hostname_ip = {}


def accept(sock, mask ):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    mes = str(conn.recv(1024), 'utf-8')
    print(mes)
    if not mes:
        sel.unregister(conn)
        conn.close()
        return 
    vals = mes.split(" ")
    if(vals[0] == '0'):#Add Entry to Table 
        hostname_ip[vals[1]] = vals[2]
        return conn.sendall(b'IP Added to DNS')
    else:
        print(vals)
        if(vals[1]) not in hostname_ip.keys():
            return conn.sendall(b"0.0.0.0")
        else:
            return conn.sendall(bytes(hostname_ip[vals[1]], 'utf-8'))


sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        # print(key)
        callback(key.fileobj, mask)


