import socket, time, _thread

def millis():
    return int(time.time()*1000)

CMD_NOP = 10
CMD_PING = 11
CMD_PING_ACK = 12
CMD_TX = 13
CMD_RQRETX = 14

def nethash(cmd, data):
    out = 0xC59638FD^cmd
    for i in data:
        a=out^(i<<1)
        a+=i<<16
        out=a^(out<<3)
    return out&0xFFFFFFFF

class BaseUplink:
    def __init__(self):
        self.queue = []
        self.inbuf = b''
        self.lstxdata = b''
        self.lstxcmd = CMD_NOP
        self.pings_accepted = 0
    def restackPacket(self, data):
        self.queue.append(data)
    def update(self):
        self.fillBuffer()
        while True:
            if len(self.inbuf)<6:
                return
            size = int.from_bytes(self.inbuf[1:3],'little')
            if len(self.inbuf)<(7+size):
                return
            cmd = self.inbuf[0]
            data = self.inbuf[3:3+size]
            h = int.from_bytes(self.inbuf[3+size:7+size],'little')
            #print("Receieved",cmd,data)#,hex(h), hex(nethash(cmd,data)))
            if h!=nethash(cmd,data):
                self.sendPacket(CMD_RQRETX,b'')
                #print("Error: hash",hex(h),"does not match",hex(nethash(cmd,data)))
            if cmd==CMD_PING:
                self.sendPacket(CMD_PING_ACK,b'')
            elif cmd==CMD_RQRETX:
                self.sendPacket(self.lstxcmd, self.lstxdata)
            elif cmd==CMD_TX:
                self.queue.append(data)
            elif cmd==CMD_PING_ACK:
                self.pings_accepted+=1
            else:
                pass
            self.inbuf = self.inbuf[7+size:]
    def available(self):
        self.update()
        return len(self.queue)
    def getPacket(self, timeout = 8000):
        if timeout==-1:
            self.enableBlocking()
        else:
            self.disableBlocking()
        self.update()
        if self.available()>0:
            self.disableBlocking()
            return self.queue.remove(0)
        timer = millis() + timeout
        while millis()<timeout:
            self.update()
            if len(self.queue)>0:
                self.disableBlocking()
                return self.queue.remove(0)
            time.sleep(0.005)
        self.disableBlocking()
        return None
    def sendData(self,data):
        self.sendPacket(CMD_TX, data)
    def sendPacket(self,cmd,data):
        packet = bytes([cmd])+len(data).to_bytes(2, 'little')+data
        packet+= nethash(cmd,data).to_bytes(4, 'little')
        self.lstxcmd = cmd
        self.lstxdata = data
        self.sendDataRaw(packet)
        #print("Sending",packet)
    def ping(self, timeout = 8000):
        disableBlocking()
        timer = millis()+timeout
        self.sendPacket(CMD_PING,b'')
        while timer>millis():
            self.update()
            if self.pings_accepted>0:
                self.pings_accepted-=1
                return timer-millis()
            time.sleep(0.001)
        return -1
    def sendDataRaw(self,data):
        print("ERROR:  Bullshit sendDataRaw function used!")
    def fillBuffer(self,data):
        print("ERROR:  Bullshit fillBuffer function used!")
    def close(self):
        print("ERROR:  Invalid close function used!")
    def enableBlocking(self):
        pass
    def disableBlocking(self):
        pass
class TcpSocketUplink(BaseUplink):
    def __init__(self, sok):
        super().__init__()
        sok.setblocking(False)
        self.sok = sok
    def fillBuffer(self):
        try:
            self.inbuf += self.sok.recv(65536)
        except BlockingIOError:
            pass
    def sendDataRaw(self,data):
        self.sok.sendall(data)
    def close(self):
        self.sok.close()
    def enableBlocking(self):
        self.sok.setblocking(True)
    def disableBlocking(self):
        self.sok.setblocking(False)
def TcpClientUplink(endpoint, port=16927):
    sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sok.connect((endpoint, port))
    return TcpSocketUplink(sok)
def neonetServer(handler,port=16927):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            print(addr,"is connecting...")
            with conn:
                uplink = TcpSocketUplink(conn)
                if uplink.ping()!=-1:
                    _thread.start_new_thread(handler,(uplink,))
                else:
                    uplink.close()
def startNeonetServerThread(handler,port=16927):
    return _thread.start_new_thread(neonetServer,(handler,port))
def test_connection(endpoint, port=1152):
    link = TcpClientUplink(endpoint,port)
    while True:
        link.update()
