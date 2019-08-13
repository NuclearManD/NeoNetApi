import neonet_raw
class InterceptedUplink(neonet_raw.BaseUplink):
    def __init__(self, uplink = None):
        super().__init__()
        self.link = uplink
        self.outPackets = []
        self.inPackets = []
    def fillBuffer(self):
        pass
    def sendDataRaw(self,data):
        self.outPackets.append(data)
        if self.link!=None:
            self.link.sendDataRaw(data)
    def getPacket(self, timeout = 8000):
        pkt = self.link.getPacket(timeout)
        if pkt!=None:
            self.inPackets.append(pkt)
        return pkt
    def close(self):
        self.link = None
    def available(self):
        return self.link.available()
    def enableBlocking(self):
        pass
    def disableBlocking(self):
        pass
