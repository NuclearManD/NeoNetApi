import sys, os
sys.path.append(os.path.abspath('../'))

import neonet, time
import netlog as logging
import filebase, remote_control
import storage, _thread

key='default-key'
adr=0xC7860010
def log_default(s):
    print(s, end='')
log = log_default

def system(cmd):
    result = ["", None]
    con = remote_control.ControlConnection(adr, key)
    con.system(cmd)
    while result[1]==None:
        data = con.sys_pull()
        if type(data)==int:
            result[1]=data
        elif data!=None:
            if data[0]=='stdo' or data[0]=='stde':
                log(data[1])
                result[0]+=data[1]
    con.close()
    return result


if __name__=="__main__":
    if os.path.isfile("client-cfg.txt"):
        cfg = storage.loadDict("client-cfg.txt")
        key = cfg['key']
        adr = cfg['adr']
    neonet.setup()
    while True:
        system(input("> "))
