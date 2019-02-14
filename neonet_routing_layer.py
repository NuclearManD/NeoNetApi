from neonet_raw import *
from random import randint

# Neonet Routing Layer should be called NRL
# Neonet Transit Layer should be called NTL

# I think most of this file will need to be rewritten at some point.
# yea this file is a mess....

# packet structure:
#
#  _________________________________________________________________________
# | cmd(8) | target_address(64) | sender_address(64) | port(32) | data (8n) \
# |________|____________________|____________________|__________|___________/
#
# since neonet's underlying transit layer keeps track of packet size, we don't need to
# include the length of the data section.
#
# 21 bytes is the minimum packet length

# commands:

CMD_CONNECT = 0x10       # establish connection
CMD_DISCONNECT = 0x11    # close connection
CMD_REDIRECT = 0x12      # change port number and address of connection
CMD_SEND_PACKET = 0x13   # send a chunk of data
CMD_SEND_RAW = 0x14      # send a chunk of data, with the other end getting the data on NTL
CMD_ACCEPT = 0x15        # accept the connection request
CMD_TAKE_ADDRESS = 0x40  # take an address on the network
CMD_ALLOC_ADDRESS = 0x41 # allocate a safe address
CMD_ALLOC_REPLY   = 0x42 # the reply command to CMD_ALLOC_ADDRESS

# common addresses

ADR_BCAST    = 0x000000FF   # All devices across the entire accessible Neonet network.
ADR_LOCAL    = 0x00000000   # this system, loopback, like localhost.   May not always work!
                            # > It is recommended to use a loopback uplink instead.
ADR_ENDPOINT = 0x00000001   # the system at the other end of the uplink

# None of the above addresses are 'absolute addresses'.  An absolute address always maps to the same device
# on the network.

ALLOC_ADR_PACKET = bytes([CMD_ALLOC_ADDRESS])+ADR_ENDPOINT.to_bytes(8,'little')+ADR_ENDPOINT.to_bytes(8,'little')+bytes(4)

def makeAddress(uplink = None):
    if uplink!=None:
        uplink.sendData(ALLOC_ADR_PACKET)
        data = uplink.getPacket(timeout = 4000)
        if data!=None and data!=-1:
            if data[0]==CMD_ALLOC_REPLY:
                return int.from_bytes(data[1:9],'little')
    return randint(0x00000100,0xFFFFFFFFFFFFFFFF)
ourAddress = makeAddress()
def setAddress(address=ourAddress,bcastAdr = False):
    if bcastAdr and isAbsoluteAddress(address):
        # take our address on the network.  If the address is already taken then
        # the connection may not work or may be unreliable.
        # For this reason be sure to get a random address or ask the endpoint to allocate you one.
        self.sendPacketRaw(CMD_TAKE_ADDRESS, ADR_BCAST, b'')
routing_table = {}
uplinks = []
def register_uplink(uplink):
    uplinks.append(uplink)
class NrlConnection:
    def __init__(self, address, port, uplink):
        self.adr = address
        self.port = port
        self.link = uplink
        self.connected = False
    def connect(self):
        self.connected = False
        self.sendPacketRaw(CMD_CONNECT, address, port, b'')
        packet = self.readPacket(8000)
        if packet!=None:
            if packet[0]==CMD_ACCEPT:
                # readPacket already checked to make sure the packet is for this connection,
                # so if we're here then we're connected.
                self.connected = True
                return True
        return False
    def readPacket(self, timeout=8000):
        timer = millis() + timeout
        while True:
            cnt = timer-millis()
            if cnt<=0:
                return None # timeout
            data = self.link.getPacket(cnt)
            if data==None or data==-1 or len(data)<21:
                return None # timeout or uplink dead, or bad packet
            result = [data[0]] # command
            result.append(int.from_bytes(data[1:9],'little'))  # target
            result.append(int.from_bytes(data[9:17],'little')) # sender
            result.append(int.from_bytes(data[17:21],'little'))# port number
            result.append(data[21:]) # data
            if result[3]==self.port and result[2]==self.adr and result[1]==ourAddress:
                return result
            elif packet[0]==CMD_TAKE_ADDRESS:
                routing_table[result[2]] = uplink
            self.link.restackData(data)
    def getData(self, timeout=8000):
        if not self.connected:
            return None
        timer = millis() + timeout
        while timer>millis():
            packet = self.readPacket(timeout)
            if packet[0]==CMD_DISCONNECT:
                self.connected = False
                return None
            elif packet[0]==CMD_REDIRECT:
                self.port = int.from_bytes(packet[4][:4],'little')
                self.adr = int.from_bytes(packet[4][4:12],'little')
            el
        return None
    def sendData()
    def disconnect(self):
        self.sendPacketRaw(CMD_DISCONNECT, address, port, b'')
        self.connected = False
    
