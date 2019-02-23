import os, sys
if os.path.isfile(os.path.abspath("../../neonet.py")) and not os.path.isfile("./neonet.py"):
    sys.path.append(os.path.abspath("../../"))

import msg_api
net = msg_api.net
from neonet_routing_layer import readRoutingTable
from random import randint

def err(*s):
    for i in s:
        sys.stderr.write(str(i)+'\n')

errored = False

args = sys.argv

routing_table_text = """
route * tcp0
"""

port = 92
adr = (randint(0,0xFFFFFFFF)<<16)|0x1000000000801F

if '-h' in args:
    # print usage here
    print("Usage: python msg_server.py [OPTIONS]")
    print("  -route [file]   :   Specify a routing file to read")
    print("  -adr [address]  :   Specify server address, random if unspecified.")
    print("  -port [port]    :   Specify server listening port")
    print("                      -> default is 92")
    print(" Server port and address are printed on program start.")
else:
    if '-route' in args:
        # read route file
        i = args.index('-route')+1
        if i>=len(args):
            err("Error: -route directive given but no file specified!")
            errored = True
        else:
            if not os.path.isfile(os.path.abspath(args[i])):
                err("Error: route file '"+args[1]+"' not found!")
                errored = True
            else:
                with open(os.path.abspath(args[i])) as f:
                    routing_table_text = f.read()
    if '-adr' in args:
        # set address
        i = args.index('-adr')+1
        if i>=len(args):
            err("Error: -adr directive given but no file specified!")
            errored = True
        else:
            try:
                s = args[i]
                if not s.startswith('0x'):
                    raise Exception()
                else:
                    adr = int(s[2:],16)
            except:
                err("Error: -arg "+s+" is not valid!  Please use a hex address.")
                errored = True
    if '-port' in args:
        # set port
        i = args.index('-port')+1
        if i>=len(args):
            err("Error: -port directive given but no file specified!")
            errored = True
        else:
            try:
                s = args[i]
                port = int(s)
            except:
                err("Error: -port "+s+" is not valid!  Please use an integer port.")
                errored = True
    if errored:
        err("There was/were error(s) starting the server!  Check your configuration.")
    else:
        print("Connecting to network...")
        net.setup(adr, routing_table=readRoutingTable(routing_table_text))
        #print("Server starting on "+hex(adr)+":"+str(port))
        msg_api.run_server(port=port)
        err("Server quit.")
    
        
