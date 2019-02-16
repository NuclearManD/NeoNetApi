package nuclaer.neonet.programs;

import java.util.Properties;

import nuclaer.neonet.routing.NrlServer;
import nuclaer.neonet.routing.UplinkManager;
import nuclaer.tk.KitFileIO;

public class NRLSwitchServer extends NrlServer {

	public NRLSwitchServer(Properties prefs_file) {
		super(Long.decode(prefs_file.getProperty("address", ""+UplinkManager.randAddress())), Integer.parseInt(prefs_file.getProperty("port", "16927")));
	}
	
	public static void exec(String path) {
		new NRLSwitchServer(KitFileIO.loadProperties(path));
	}
	public static void main(String[] args) {
		exec("config/switch.cfg");
	}
}
