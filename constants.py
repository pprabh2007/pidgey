#colors
SUCCESS='green'
FAILURE='red'
DEBUG='cyan'
RETRY='yellow'

TIMEOUT_PERIOD = 16
SYNCING_PERIOD = 8

ORIGIN_SERVERS_STORE_CREDENTIALS = [("localhost", 9999), ("localhost", 8999)]
ORIGIN_SERVERS_REQUEST_CREDENTIALS = [("localhost", 10000), ("localhost", 9000)]
SYNC_PORT_1 = 10001
SYNC_PORT_2 = 10002
NO_OF_ORIGIN_SERVERS = 2

EDGE_SERVERS_REQUEST_CREDENTIALS = [("localhost", 10005), ("localhost", 10006)]
NO_OF_EDGE_SERVERS = 2

FILE_FOUND = "FOUND"
FILE_NOT_FOUND = "NOTFOUND"

# Load balancer
LOAD_IP = '127.0.0.1'
LOAD_BACKUP_IP = '127.0.0.1'
BACKUP_PORT = 6669
EDGE_PORT = 6542
BEDGE_PORT = 6642
CLIENT_PORT = 6543
BCLIENT_PORT = 6643
EDGE_MAX = 100
WEIGHT_DISTANCE = 0.8
WEIGHT_LOAD = 0.2
MAX_CLIENT_REQUESTS= 10
EDGE_HEARTBEAT_TIME=1
LB_HEARTBEAT_TIME = 1
LB_DOMAIN = "www.pidgey.com"

# Edge Server
MSG_DELAY = 5
EDGE_HEARTBEAT_TIME = 1

# DNS server
DNS_IP = '127.0.0.1'
DNS_PORT = 6550
DNS_MAX_LISTEN = 100
MAXLEN_DOMAIN = 249

# location coordinates
LOCATION = {}
LOCATION[0] = (0.,0.)
LOCATION[1] = (0.,1.)
LOCATION[2] = (1.,0.)
LOCATION[3] = (1.,1.)