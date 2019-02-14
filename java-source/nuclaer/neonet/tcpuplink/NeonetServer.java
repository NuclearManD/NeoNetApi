package nuclaer.neonet.tcpuplink;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;

public abstract class NeonetServer implements Runnable{
	
	private int port = 16927;
	
	public abstract void onNewConnection(Uplink uplink);
	
	protected void debug(String s) {
		// do nothing, this function can be overridden for logs
	}
	
	protected Thread serverThread = null;
	
	protected ArrayList<Thread> subthreads = new ArrayList<Thread>();

	public NeonetServer() {
		serverThread = new Thread(this);
		serverThread.start();
	}
	public NeonetServer(int port) {
		this.port = port;
		serverThread = new Thread(this);
		serverThread.start();
	}
	
	protected boolean running = true;
	
	public final void run() {
		try {
			ServerSocket socket = new ServerSocket(port);
			debug("Server started.");
			while(running) {
				Socket client = socket.accept();
				debug("Incoming connection...");
				Uplink uplink = new SocketUplink(client);
				if(uplink.ping()>0) {
					debug("New connection accepted from "+socket.getInetAddress().toString());
					onNewConnection(uplink);
				} else {
					debug("Connection ping failed.");
					client.close();
				}
			}
			socket.close();
		} catch (IOException e) {
			debug("Error occurred in server thread! Stopping!");
		}
		running = false;
	}
}
