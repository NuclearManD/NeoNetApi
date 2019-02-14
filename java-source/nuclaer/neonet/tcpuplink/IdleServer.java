package nuclaer.neonet.tcpuplink;

public class IdleServer extends NeonetServer {
	public IdleServer() {
		super(1152);
	}
	public void onNewConnection(Uplink uplink) {
		while(true) {
			uplink.getPacket(10000);
			if(uplink.ping()==-1)break;
		}
		uplink.close();
		System.out.println("Connection terminated (ping failed).");
	}
	
	protected void debug(String s) {
		System.out.println(s);
	}
	public static void main(String[] args) {
		new IdleServer();
	}
}
