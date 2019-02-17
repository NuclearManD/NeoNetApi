import neonet as net
import time
from random import randint
def millis():
    return int(time.time()*1000)
# Messenger Protocol:
#
#  Client sends a packet to the listening port with the data being b'MSG_CON'
#  Server replies on same port: four bytes for port (little endian) if accepted, no
#   response if connection is denied.
#  Client and server open connections on the given port for communication
#  Client sends commands to the server and the server sends message packets to the client.

CMD_WRITE_MESSAGE = 0x20
CMD_READ_ALL = 0x30
CMD_GET_CHANNELS = 0x

MSG_PORT = 92

def get_rand_port():
    return randint(0x1000,0x7FFFFFFF)

def run_server():
    net.setup()
    scon = net.NrlOpenPort(MSG_PORT)
    cons = []

    messages = []
    
    while True:
        if
        for i in cons:
            # update the connection because a packet is available
        if scon.available():
            pk = scon.recv(0)
            if pk[1]==b'MSG_CON':
                port = get_rand_port()
                scon.send(pk[0],port.to_bytes(4,'little'))
                cons.append(net.NrlConnection(pk[0],port))
