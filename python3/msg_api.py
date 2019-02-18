import neonet as net
import time, _thread
from random import randint
def millis():
    return int(time.time()*1000)
# Messenger Protocol:
#
#  Client sends a packet to the listening port with the data being b'MSG_CON:[username]'
#  Server replies on same port: four bytes for port (little endian) if accepted, no
#   response if connection is denied.
#  Client and server open connections on the given port for communication
#  Client sends commands to the server and the server sends message packets to the client.

CMD_WRITE_MSG = 0x20
CMD_READ_ALL = 0x30

MSG_PORT = 92

def get_rand_port():
    return randint(0x1000,0x7FFFFFFF)
def __sendMsgPkt(con, msg):
    con.send(msg[0].to_bytes(8,'little')+msg[1])
def __msgBcast(cons, msg_txt):
    msg = [millis(), msg_txt]
    for i in cons:
        __sendMsgPkt(i,msg)
    return msg
def run_server(adr = net.address, port = MSG_PORT):
    net.setup(adr)
    scon = net.NrlOpenPort(port)
    cons = []

    messages = []

    users = {}
    
    while True:
        for i in cons:
            if i.available():
                # update the connection because a packet is available
                packet = i.recv()
                cmd = packet[0]
                packet = packet[1:]
                if cmd==CMD_WRITE_MSG:
                    messages.append(__msgBcast(cons, users[i.adr]+b": "+packet))
                    print((users[i.adr]+b": "+packet).decode())
                elif cmd==CMD_READ_ALL:
                    for i2 in messages:
                        __sendMsgPkt(i,i2)
                else:
                    print("Invalid packet receieved from "+users[i.adr].decode()+" : "+repr(packet))
        if scon.available():
            pk = scon.recv(0)
            if pk[1].startswith(b'MSG_CON') and pk[1][7]==58:
                port = get_rand_port()
                scon.send(pk[0],port.to_bytes(4,'little'))
                cons.append(net.NrlConnection(pk[0],port))
                user = pk[1][8:]
                print("New connection from "+hex(pk[0])+" ["+user.decode()+"]")
                users[pk[0]]=user
                messages.append(__msgBcast(cons, user+b' is now online.'))
        time.sleep(0.001)
def start_server_thread(adr = net.address, port = MSG_PORT):
    return _thread.start_new_thread(run_server,(adr, port))

class MessagingClient:
    def __init__(self, adr, username, port = MSG_PORT):
        self.con = net.NrlConnection(adr, port)
        self.con.send(b'MSG_CON:'+username.encode())
        time.sleep(0.001)
        pkt = self.con.recv(8000)
        if pkt==None:
            raise Exception("Connection Refused")
        if len(pkt)!=4:
            raise Exception("Invalid Response Received: "+repr(pkt))
        self.con.port = int.from_bytes(pkt, 'little')
        self.con.send(bytes([CMD_READ_ALL]))
        self.ls_time = 0
        self.ls_index = 0
        self.list_text = []
        self.list_time = []
    def update(self):
        while self.con.available():
            pkt = self.con.recv(0)
            #print(pkt)
            timing = int.from_bytes(pkt[:8],'little')
            if timing in self.list_time:
                #print("Same time.")
                continue
            msg_text = pkt[8:].decode()
            if len(self.list_time)==0 or timing>self.list_time[len(self.list_time)-1]:
                self.list_time.append(timing)
                self.list_text.append(msg_text)
                continue
            else:
                for i in range(len(self.list_time)):
                    if self.list_time[i]>timing:
                        self.list_time.insert(i, timing)
                        self.list_text.insert(i, msg_text)
                        break
    def send_msg(self, text):
        self.con.send(bytes([CMD_WRITE_MSG])+text.encode())
    def pop_msg(self):
        self.update()
        for i in range(self.ls_index,len(self.list_time)):
            if self.list_time[i]>self.ls_time:
                self.ls_time = self.list_time[i]
                self.ls_index = i
                return self.list_text[i]
        return None
    def seek(self, timing):
        self.ls_time = timing
        self.ls_index = 0
    def print_new(self):
        while True:
            in_msg=self.pop_msg()
            if in_msg==None:
                break
            print(in_msg)
