package nuclaer.neonet.programs;

import nuclaer.tk.KitFileIO;

public class Main {

	public static void main(String[] args) {
		if(args.length==0) {
			args = new String[1];
			args[0] = "config/switch.cfg";
			System.out.println("Using "+args[0]+" as default config file for NRL Switch Server (config path unspecified)");
			System.out.println("If it does not exist then default values will be used.");
		}
		new NRLSwitchServer(KitFileIO.loadProperties(args[0]));
	}

}
