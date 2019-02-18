package nuclaer.neonet.routing;

import java.util.ArrayList;

public class NrlConnection {
	UplinkManager manager;
	public long adr, port;
	
	ArrayList<NrlPacket> queue = new ArrayList<NrlPacket>();
	public NrlConnection(UplinkManager man, long address, long port) {
		manager = man;
		adr =address;
		this.port = port;
	}
	public boolean send(byte[] data) {
		return manager.sendPacket(new NrlPacket(manager.address,adr, port, data));
	}
	public byte[] recv() {
		return recv(8000);
	}
	public byte[] recv(long timeout) {
		if(available()>0)
            return queue.remove(0).data;
        else {
            long timer = System.currentTimeMillis()+timeout;
            while (timer>System.currentTimeMillis()){
                if(available()>0)
                    return queue.remove(0).data;
                Thread.yield();
            }
            return null;
        }
	}
	public int available() {
		int i=0;
        while(i<manager.available()) {
        	NrlPacket pkt = manager.incoming.get(i);
            if(pkt.sender==adr&&pkt.port==port)
                queue.add(manager.incoming.remove(i));
            else
                i++;
        }
        return queue.size();
	}
}
