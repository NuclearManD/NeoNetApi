
import socket, neonet, random, os, time, subprocess
from netlog import log, add_log_file

from kryptonite import CryptFS

DEFAULT_PORT = 87

def handle_client(fs, con, adr):
    log("Filebase: Accepted connection from "+str(adr))
    running = True
    while running:
        data = con.recv(60000)
        if data==None:
            con.send(b"HELLO?")
            data = con.recv(5000)
            if data==None:
                break
            if data!=b"HELLO!":
                con.queue.append(data) # put it back on if it's not a response
        elif data[:5]==b'CLOSE':
            txt = "Filebase: "+str(adr)+" is closing the connection."
            if len(data)>5:
                txt+="  Message = "+data[5:].decode()
            log(txt)
            break
        elif data[:2]==b"WR":
            try:
                idx = data.find(b';')
                fn = data[2:idx].decode()
                fs.write(fn, data[idx:])
                con.send(b"OK")
            except Exception as e:
                con.send(b"ERROR: "+str(e).encode())
        elif data[:2]==b"RD":
            try:
                fn = data[2:].decode()
                data = fs.read(fn)
                if data==-1:
                    con.send(b"FNF") # file not found
                else:
                    con.send((len(data)//8192 +1).to_bytes(4, "big"))
                    for i in range((len(data)//8192 +1)):
                        con.send(data[i*8192:(i+1)*8192])
            except Exception as e:
                con.send(b"ERROR: "+str(e).encode())
    log("Filebase: Connection to "+str(adr)+" is closed.")
def run(key, location, port = DEFAULT_PORT):
    scon = neonet.NrlOpenPort(port)

    fs = CryptFS(key, location)
    
    while True:
        data = scon.recv(float('inf'))
        adr = data[0]
        data = data[1]
        try:
            if data==b"REMOTE_CONNECT":
                port = random.randint(8192, 2**30)
                scon.send(adr, b"OK="+hex(port).encode())
                con = neonet.NrlSecureConnection(adr, port, key, 500)
                #_thread.start_new_thread(handle_client, (fs, con, adr))
                handle_client(fs, con, adr)
            else:
                log("Strange data from "+str(adr)+" : "+data.decode())
        except:
            pass
class FilebaseConnection:
    def __init__(self, adr, key, port = DEFAULT_PORT):
        tmp = neonet.NrlConnection(adr, port)
        tmp.send(b"REMOTE_CONNECT")
        data = tmp.recv()
        if data==None:
            raise Exception("Connection Refused")
        elif data[:3]!=b"OK=":
            #print(data)
            raise Exception("Remote Protocol Invalid")
        port = int(data[5:],16)
        self.con = neonet.NrlSecureConnection(adr, port, key)
    def close(self, message = ''):
        self.con.send(b'CLOSE'+message.encode())
        self.con=None
    def read(self, fn):
        self.con.send(b'RD'+fn.encode())
        buffer = b''
        data = self.con.recv()
        if data==None:
            return None
        elif data==b"FNF":
            return -1
        size = int.from_bytes(data, 'big')
        for i in range(size):
            buffer+=self.con.recv()
        return buffer
    def write(self, fn, data):
        if type(data)==str:
            data = data.encode()
        self.con.send(b'WR'+fn.encode()+b';'+data)
        msg = self.con.recv()
        if msg!=b"OK":
            if msg!=None:
                msg = msg.decode()
            return msg
if __name__=="__main__":
    add_log_file("logs/filebase/{}.txt")
    log("Starting NeoNet...")
    neonet.setup(0x880210)
    log("Starting filebase.py [default configuration]...")
    try:
        run("password", "filebase_default/") # TODO: fix this somehow
    except Exception as e:
        log("ERROR: Server threw an exception: "+str(e))
        nope()
