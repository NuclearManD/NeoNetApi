from neonet import NrlConnection

LOGREAD_PORT = 181

class LogReader:
    def __init__(self, adr, port=LOGREAD_PORT):
        self.con = NrlConnection(adr,port)
        self.con.send(b'?')
        if(b'OK'!=self.con.recv(8000)):
            raise Exception("No Response")
    def readLog(self):
        self.con.send(b'\x28')
        pkts = int(self.con.recv().decode())
        out = ''
        for i in range(pkts):
            out+=self.con.recv().decode()
        return out
    def clearLog(self):
        self.con.send(b'\x38')
        return self.con.recv()==b'OK'
