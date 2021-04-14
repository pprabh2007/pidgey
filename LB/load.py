
import socket
from threading import Timer, Thread, Lock
import time

LOAD_IP = '127.0.0.1'
EDGE_PORT = 6542
EDGE_MAX = 100


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
    print(conn)

establish_edge()