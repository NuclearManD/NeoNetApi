package nuclaer.neonet.transport;

public abstract class Uplink {
	public static int CMD_NOP = 10;
	public static int CMD_PING = 11;
	public static int CMD_PING_ACK = 12;
	public static int CMD_TX = 13;
	public static int CMD_RQRETX = 14;
	
	public abstract byte[] getPacket(int timeout);
	public abstract void sendPacket(int cmd, byte[] data);
	public abstract long ping();
	public abstract void resendPacket();
	
	public byte[] parsePacket(int cmd, byte[] data) {
		if(cmd==CMD_PING) {
			sendPacket(CMD_PING_ACK,new byte[0]);
		}else if(cmd==CMD_RQRETX){
			resendPacket();
		}else if(cmd==CMD_TX) {
			return data;
		}else if(cmd==CMD_NOP) {
			
		}
		return null;
	}
	
	public void sendData(byte[] data) {
		sendPacket(CMD_TX,data);
	}
	
	public boolean connect() {
		for(int i=0;i<4;i++) {
			if(ping()>=0)return true;
		}
		return false;
	}
	public int nethash(int cmd, byte[] data) {
		int out = 0xC59638FD^cmd;
		for(int i:data) {
			i&=0xFF;
			int a=out^(i<<1);
			a+=i<<16;
			out=a^(out<<3);
		}
		return out;
	}
	public abstract void close();
}
