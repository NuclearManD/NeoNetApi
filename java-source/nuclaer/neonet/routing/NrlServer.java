package nuclaer.neonet.routing;

import nuclaer.neonet.tcpuplink.NeonetServer;
import nuclaer.neonet.transport.Uplink;

public class NrlServer extends NeonetServer {
	UplinkManager manager;
	public NrlServer(long address, int tcp_port) {
		super(tcp_port);
		manager = new UplinkManager(address);
		manager.startUpdateThread();
	}
	public NrlServer(long address) {
		manager = new UplinkManager(address);
		manager.startUpdateThread();
	}
	public NrlServer() {
		manager = new UplinkManager(UplinkManager.randAddress());
		manager.startUpdateThread();
	}

	public void onNewConnection(Uplink uplink) {
		if(uplink.ping()!=-1) {
			manager.addUplink(uplink);
			debug("New connection.");
		}
	}
	protected void debug(String s) {
		System.out.println(s);
	}

}
