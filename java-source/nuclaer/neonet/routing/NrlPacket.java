package nuclaer.neonet.routing;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

/**
 * NRL packet object
 * @author nuclaer
 *
 */
public class NrlPacket {
	public byte[] data;
	public long sender;
	public long target;
	public long port; // long because Java doesn't support 32-bit unsigned ints >:/
	/**
	 * Decode raw neonet NTL packet into an NRL packet
	 * @param raw raw packet data
	 */
	public NrlPacket(byte[] raw){
		ByteBuffer buf = ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN);
		target = buf.getLong();
		sender = buf.getLong();
		port = buf.getInt();
		if(port<0)port+=0x100000000L;
		data = Arrays.copyOfRange(raw, 20, raw.length);
	}
	public NrlPacket(long sender, long target, long port, byte[] data) {
		this.sender = sender;
		this.target = target;
		this.port = port;
		this.data = data;
	}
	
	public String toString() {
		return "NRL Packet from "+Long.toHexString(sender)+" to "+Long.toHexString(target)+" on port "+port+", "+data.length+" bytes of data";
	}
	public byte[] encode() {
		ByteBuffer buf = ByteBuffer.allocate(20+data.length).order(ByteOrder.LITTLE_ENDIAN);
		buf.putLong(target).putLong(sender).putInt((int)port).put(data);
		return buf.array();
	}
}
