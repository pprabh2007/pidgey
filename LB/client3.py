import sys
sys.path.insert(0, "../")
import socket
from Messages.edge_LB import *
from Messages.client_LB import *

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 6543        # The port used by the server


def connectLB():

    """
    Method to connect to LBs
    IP blocks contains the DNS response
    """

    err_count = 0

    host= HOST
    port = PORT

    s = socket.socket()
    try:
        print("Connecting ",host,":",port)
        s.connect((host, port))
        print("Connected ",host,":",port)
    except socket.error:
        err_count += 1
        print("Connection failed ",host,":",port)

    if err_count == 2:
        print("Load Balancer could not be reached!")
        return s,0
    else:
        print("Connection established to the load balancer")
        return s,1

while True:
    contentreq = input("Enter content id: ")
    try:
        contentReq = int(contentreq)
    except:
        print("Enter only numbers.")
        continue
    if(contentReq<=0):
        print("Content id cannot be less than 1")
        continue


    seqNo = -1
    location_id = 0
    n_msg = Client_LB_req(contentReq,location_id)
    prev_edge_ip = n_msg.prev_edge_ip
    while True:
        # seqNo = requestFile(msg.ip, EDGE_SERVER_PORT ,contentReq)
        if seqNo != -2:
            ## TO DO get new edge server from load balancer
            s, err = connectLB()
            if err==0:
                input("Load Balancer could not be reached!")
            n_msg = Client_LB_req(contentReq,location_id,prev_edge_ip)
            try:
                input("Press enter to request new edge server")
                n_msg.send(s)
                print('Hi')
                n_msg = Client_LB_res()
                n_msg.receive(s)
                prev_edge_ip = n_msg.ip
                print(prev_edge_ip, n_msg.port)
                input("Press enter to connect to edge server!")
                if n_msg.ip=='0.0.0.0':
                    print("No edge servers available.")
                    input("Press enter to try again!")
                    continue

                # seqNo = requestFile(n_msg.ip, EDGE_SERVER_PORT ,contentReq, seqNo+1)
                seqNo = seqNo+1
            except:
                print("Error communicating with LB")
                input("Press enter to request another/same file!")
                # break
            s.close()
        else:
            break