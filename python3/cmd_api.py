import neonet as net
import time, _thread, crypt_api as crypt
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

CMD_PORT = 103

def get_rand_port():
    return randint(0x1000,0x7FFFFFFF)
def __cmdBcast(cons, cmd, password):
    text = crypt.encrypt1(millis().to_bytes(8,'little')+cmd, password)
    for i in cons:
        i.send(text)
    return cmd
def run_server(adr = net.address, port = CMD_PORT, password = ""):
    password = crypt.shortstrhash(password)
    net.setup(adr)
    print("Starting command-issuing server at "+hex(net.address)+":"+str(port))
    scon = net.NrlOpenPort(port)
    cons = []
    
    while True:
        for i in cons:
            if i.available():
                # update the connection because a packet is available
                packet = i.recv()
                try:
                    packet = crypt.decrypt1(packet, password)
                except:
                    continue
                timing = int.from_bytes(packet[:8],'little')
                if timing<millis() and timing>millis()-5000:
                    __cmdBcast(cons, packet[8:],password)
                try:
                    print(hex(i.adr)+" : issued command: "+packet[8:].decode())
                except:
                    print(hex(i.adr)+" : issued a binary command.")
        if scon.available():
            pk = scon.recv(0)
            remote_adr = pk[0]
            timing = int.from_bytes(pk[1][:8],'little')
            if timing<millis() and timing>millis()-5000:
                expected = crypt.sha512(hex(timing)+password)
                if expected == pk[1][8:]:
                    port = get_rand_port()
                    scon.send(pk[0],port.to_bytes(4,'little'))
                    cons.append(net.NrlConnection(pk[0],port))
                    print("New connection from "+hex(pk[0]))
                else:
                    print("Connection failure from "+hex(pk[0])+": bad cryptographic sequence.")
            else:
                print("Connection failure from "+hex(pk[0])+": expired timing.")
        time.sleep(0.001)
def start_server_thread(adr = net.address, port = CMD_PORT):
    return _thread.start_new_thread(run_server,(adr, port))

class CommandClient:
    def __init__(self, adr, password, port = CMD_PORT):
        self.pss = crypt.shortstrhash(password)
        self.con = net.NrlConnection(adr, port)
        self.con.send(millis().to_bytes(8,'little')+crypt.sha512(hex(millis())+self.pss))
        time.sleep(0.001)
        pkt = self.con.recv(8000)
        if pkt==None:
            raise Exception("Connection Refused")
        if len(pkt)!=4:
            raise Exception("Invalid Response Received: "+repr(pkt))
        self.con.port = int.from_bytes(pkt, 'little')
        self.queue = []
    def update(self):
        while self.con.available():
            pkt = self.con.recv(0)
            self.__decode__(pkt)
    def __decode__(self, packet):
        try:
            packet = crypt.decrypt1(packet, self.pss)
        except:
            return
        timing = int.from_bytes(packet[:8],'little')
        if timing<millis() and timing>millis()-5000:
            self.queue.insert(0,packet[8:])
    def issue_command(self, cmd):
        if type(cmd)==str:
            cmd = cmd.encode()
        self.con.send(crypt.encrypt1(millis().to_bytes(8,'little')+cmd,self.pss))
    def get_cmd(self, timeout):
        timeout+=millis()
        while timeout>millis():
            self.update()
            if len(self.queue)>0:
                return self.queue.pop()
            time.sleep(0.001)
        return None
