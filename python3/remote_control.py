
import socket, neonet, random, os, time, subprocess
from netlog import log, add_log_file

DEFAULT_PORT = 157

def handle_client(con, adr):
    log("Remote Control: Accepted connection from "+str(adr))
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
            txt = "Remote Control: "+str(adr)+" is closing the connection."
            if len(data)>5:
                txt+="  Message = "+data[5:].decode()
            log(txt)
            break
        elif data[:3]==b"CWD":
            try:
                os.chdir(data[3:].decode())
                con.send(b"OK")
            except Exception as e:
                con.send(b"ERROR: "+str(e).encode())
        elif data[:3]==b"SYS":
            try:
                con.send(b"OK")
                cmd = data[3:].decode()
                log("Executing command: "+cmd)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while p.poll()==None:
                    d = p.stdout.read()
                    if len(d)>0:
                        con.send(b'stdo='+d)
                    time.sleep(.1)
                con.send(b"done="+str(p.poll()).encode())
            except Exception as e:
                con.send(b"ERROR: "+str(e).encode())
    log("Remote Control: Connection to "+str(adr)+" is closed.")
def run(key, port = DEFAULT_PORT):
    scon = neonet.NrlOpenPort(port)
    while True:
        data = scon.recv(float('inf'))
        adr = data[0]
        data = data[1]
        try:
            if data==b"REMOTE_CONNECT":
                port = random.randint(8192, 2**30)
                scon.send(adr, b"OK="+hex(port).encode())
                con = neonet.NrlSecureConnection(adr, port, key, 500)
                #_thread.start_new_thread(handle_client, (con, adr))
                handle_client(con, adr)
            else:
                log("Strange data from "+str(adr)+" : "+data.decode())
        except:
            pass
class ControlConnection:
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
    def cwd(self, wd):
        self.con.send(b'CWD'+wd.encode())
        msg = self.con.recv()
        if msg!=b"OK":
            if msg!=None:
                msg = msg.decode()
            return msg
    def system(self, cmd):
        self.con.send(b'SYS'+cmd.encode())
        msg = self.con.recv()
        if msg!=b"OK":
            if msg!=None:
                msg = msg.decode()
            return msg
    def sys_pull(self):
        d = self.con.recv(200)
        if d!=None:
            d=d.decode()
            cmd = d[:5]
            if cmd=="stdo=":
                return ['stdo',d[5:]]
            elif cmd=="stde=":
                return ['stde',d[5:]]
            elif cmd=="done=":
                return int(d[5:])
if __name__=="__main__":
    add_log_file("logs/{}.txt")
    log("Starting NeoNet...")
    neonet.setup(0x880210)
    log("Starting remote_control.py ...")
    try:
        run("password") # TODO: fix this somehow
    except Exception as e:
        log("ERROR: Server threw an exception: "+str(e))
        nope()
