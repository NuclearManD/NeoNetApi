package nuclaer.neonet.tcpuplink;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;

import nuclaer.neonet.transport.Uplink;

public class SocketUplink extends Uplink {
	private Socket socket;
	private volatile boolean rxa = false;
	public SocketUplink(Socket sok) {
		try {
			socket = sok;
			if(!connect())
				socket.close(); // bad protocol
		}catch(Exception e) {
			
		}
	}
	
	public byte[] getPacket(int timeout) {
		if(queue.size()>0)return queue.remove(0);
		if(socket.isClosed()||!socket.isConnected())
			return null;
		long timer = System.currentTimeMillis()+timeout;
		try {
			InputStream is = socket.getInputStream();
			while(timer>System.currentTimeMillis()) {
				while(rxa) {
					if(timer<System.currentTimeMillis())return null;
				}
				if(is.available()>6) {
					rxa=true;
					long packet_timer = System.currentTimeMillis()+1000;
					int cmd = is.read();
					if((cmd<10)||(cmd>37))continue;
					int len = is.read();
					len |= is.read()<<8;
					byte[] buf = new byte[len];
					int read = 0;
					while(read<len && (packet_timer>System.currentTimeMillis())){
						int q=is.read(buf, read, buf.length-read);
						if(q==-1)return null;
						read+=q;
					}
					byte[] hashbuf = new byte[4];
					read = 0;
					while(read<4 && (packet_timer>System.currentTimeMillis())){
						int q=is.read(hashbuf, read, 4-read);
						if(q==-1)return null;
						read+=q;
					}
					rxa=false;
					int hash = ByteBuffer.wrap(hashbuf).order(ByteOrder.LITTLE_ENDIAN).getInt();
					if(hash!=nethash(cmd, buf)) {
						sendPacket(CMD_RQRETX,new byte[0]);
						continue;
					}else {
						byte[] data = parsePacket(cmd,buf);
						if(data!=null)return data;
					}
				}
				Thread.sleep(1);
				if(socket.isClosed()||!socket.isConnected()) {
					return null;
				}
			}
		}catch(Exception e) {
			
		}
		return null;
	}
	int lscmd;
	byte[] lsdata;

	public void sendPacket(int cmd, byte[] data) {
		if(socket.isClosed()||!socket.isConnected())
			return;
		if(cmd!=CMD_RQRETX) {
			lscmd = cmd;
			lsdata = data;
		}
		try {
			OutputStream os = socket.getOutputStream();
			synchronized(this) {
				os.write(cmd);
				os.write(data.length&255);
				os.write(data.length>>8);
				os.write(data);
				os.flush();
				int hash = nethash(cmd,data);
				os.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(hash).array());
				os.flush();
			}
		}catch(Exception e) {
			
		}finally {
		}
	}

	public long ping() {
		if(socket.isClosed()||!socket.isConnected()) {
			return -1;
		}
		long timer = System.currentTimeMillis()+8000;
		long time = System.currentTimeMillis();
		sendPacket(CMD_PING, new byte[0]);
		try {
			InputStream is = socket.getInputStream();
			while(timer>System.currentTimeMillis()) {
				while(rxa) {
					if(timer<System.currentTimeMillis())return -1;
				}
				if(is.available()>6) {
					rxa=true;
					long packet_timer = System.currentTimeMillis()+1000;
					int cmd = is.read();
					if((cmd<10)||(cmd>37))continue;
					int len = is.read();
					len |= is.read()<<8;
					byte[] buf = new byte[len];
					int read = 0;
					while(read<len && (packet_timer>System.currentTimeMillis())){
						int q=is.read(buf, read, buf.length-read);
						if(q==-1)return -1;
						read+=q;
					}
					byte[] hashbuf = new byte[4];
					read = 0;
					while(read<4 && (packet_timer>System.currentTimeMillis())){
						int q=is.read(hashbuf, read, 4-read);
						if(q==-1)return -1;
						read+=q;
					}
					rxa=false;
					int hash = ByteBuffer.wrap(hashbuf).order(ByteOrder.LITTLE_ENDIAN).getInt();
					if(hash!=nethash(cmd, buf)) {
						System.out.println("Got bad packet, requesting retransmission...");
						System.out.println("\texpected |   got");
						//System.out.println("length\t"+len+"\t | "+read);
						System.out.println("hash\t"+hash+"\t | "+nethash(cmd, buf));
						System.out.println("Cmd was "+cmd);
						for(byte i:buf) {
							System.out.print(Integer.toHexString(((int)i)&0xFF)+", ");
						}
						System.out.println();
						
						sendPacket(CMD_RQRETX,new byte[0]);
						continue;
					}else if(cmd==CMD_PING_ACK){
						return System.currentTimeMillis()-time;
					}else {
						byte[] data = parsePacket(cmd,buf);
						if(data!=null)queuePacket(data);
					}
				}
				Thread.sleep(1);
				if(socket.isClosed()||!socket.isConnected()) {
					return -1;
				}
			}
		}catch(Exception e) {
			
		}
		return -1;
	}

	ArrayList<byte[]> queue = new ArrayList<byte[]>();
	
	private void queuePacket(byte[] data) {
		queue.add(data);
	}

	public void resendPacket() {
		sendPacket(lscmd,lsdata);
	}

	public void close() {
		try {
			socket.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public static Uplink connect(String endpoint) {
		Socket socket;
		try {
			socket = new Socket(endpoint, 16927); // old port for Matrix was 7129.  This is the Neonet port.
		} catch (UnknownHostException e) {
			e.printStackTrace();
			return null;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
		return new SocketUplink(socket);
	}
	
	public static Uplink connect(String endpoint, int port) {
		Socket socket;
		try {
			socket = new Socket(endpoint, port); // old port for Matrix was 7129.  This is the Neonet port.
		} catch (UnknownHostException e) {
			e.printStackTrace();
			return null;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
		return new SocketUplink(socket);
	}

}
