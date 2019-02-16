package nuclaer.neonet.routing;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

import nuclaer.neonet.transport.Uplink;

public class UplinkManager implements Runnable{
	HashMap<String, Uplink> uplinks = new HashMap<String, Uplink>();
	HashMap<Long, String> routes = new HashMap<Long, String>();
	
	ArrayList<NrlPacket> incoming = new ArrayList<NrlPacket>();
	int lsid = 0;
	long address;
	public UplinkManager(long address) {
		this.address = address;
	}
	public void addUplink(Uplink uplink) {
		addUplink(""+(lsid++),uplink);
	}
	public void addUplink(String key, Uplink uplink) {
		uplinks.put(key, uplink);
		debug("New uplink '"+key+"'");
		ByteBuffer buf = ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN);
		buf.putLong(address>>16);
		uplink.sendData(Arrays.copyOf(buf.array(),6));
	}
	public void addRoute(long area_code, String key) {
		debug("New connection to "+Long.toHexString(area_code));
		routes.put(area_code&0xFFFFFFFFFFFFL, key);
	}
	public void update() {
		for(String i:uplinks.keySet()) {
			Uplink u = uplinks.get(i);
			byte[] data = u.getPacket(1);
			if(data!=null) {
				//debug(Arrays.toString(data));
				if(data.length==6)addRoute(ByteBuffer.wrap(Arrays.copyOf(data,8)).order(ByteOrder.LITTLE_ENDIAN).getLong(),i);
				else if(data.length>=20) {
					NrlPacket packet = new NrlPacket(data);
					if(packet.target == address) {
						// it's for this system
						debug("Got: "+packet);
						incoming.add(packet);
					}else {
						long ac = packet.target>>16;
						if(routes.containsKey(ac)) { // only transmit if we have a route for it
							String key = routes.get(ac); // we have the route!
							if((key!=i)&&uplinks.containsKey(key)) {// transmit to a different uplink or don't transmit at all
								uplinks.get(key).sendData(data); // send the raw packet
							}
						}
					}
				}
			}
		}
	}
	private void debug(String s) {
		System.out.println(s);
	}
	public int available() {
		if(!updateThreadRunning)update();
		return incoming.size();
	}

	public NrlPacket getPacket() {
		if(0<available())return incoming.remove(0);
		return null;
	}

	public NrlPacket getPacket(long timeout) {
		long timer = timeout+System.currentTimeMillis();
		do {
			Thread.yield();
			if(0<available())return incoming.remove(0);
		}while(System.currentTimeMillis()<timer);
		return null;
	}
	/**
	 * Transmit a packet using NRL
	 * @param packet The packet to send
	 * @return if next endpoint was resolved (success/fail)
	 */
	public boolean sendPacket(NrlPacket packet) {
		long ac = packet.target>>16;
		if(routes.containsKey(ac)) { // only transmit if we have a route for it
			String key = routes.get(ac); // we have the route!
			if(uplinks.containsKey(key)) {// transmit to a different uplink or don't transmit at all
				uplinks.get(key).sendData(packet.encode()); // send the raw packet
				return true;
			}
		}
		return false;
	}
	
	public boolean updateThreadRunning = false;
	// this run method continually updates the UplinkManager
	public void run() {
		if(updateThreadRunning)return;
		updateThreadRunning = true;
		while(updateThreadRunning) {
			update();
			Thread.yield();
		}
	}
	public Thread startUpdateThread() {
		Thread t = new Thread(this);
		t.start();
		return t;
	}
	public static long randAddress() {
		return (((int)(0x7FFFFFFFFFFFL*Math.random()))<<16)|1;
	}
}
