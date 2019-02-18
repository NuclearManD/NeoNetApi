package nuclaer.neonet.protocol;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Arrays;

import nuclaer.neonet.routing.NrlConnection;
import nuclaer.neonet.routing.UplinkManager;

public class MessagingClient {
	public static byte CMD_WRITE_MSG = 0x20;
	public static byte CMD_READ_ALL[] = {0x30};
	
	public static byte MSG_PORT = 92;
	
	private NrlConnection con;
	private int index = 0;
	private long ls_time = 0;

	private ArrayList<Long> msg_times = new ArrayList<Long>();
	private ArrayList<String> msg_texts = new ArrayList<String>();

	public MessagingClient(UplinkManager man, long address, String username, long port) {
		setup(man, port, address, username);
	}
	public MessagingClient(UplinkManager man, long address, String username) {
		setup(man, MSG_PORT, address, username);
	}

	private void setup(UplinkManager man, long port, long address, String username) {
		con = new NrlConnection(man, address, port);
		con.send(("MSG_CON:"+username).getBytes());
		byte[] response = con.recv(8000);
		if(response==null||response.length!=4) {
			con=null;
			return;
		}
		con.port = 0xFFFFFFFFL&((long)ByteBuffer.wrap(response).order(ByteOrder.LITTLE_ENDIAN).getInt());
		con.send(CMD_READ_ALL);
	}
	public void update() {
		while(con.available()>0) {
			ByteBuffer pkt = ByteBuffer.wrap(con.recv(0));
			long timing = pkt.order(ByteOrder.LITTLE_ENDIAN).getLong();
			if(msg_times.contains(timing))continue;
			String text = new String(Arrays.copyOfRange(pkt.array(), 8, pkt.capacity()));
			if(msg_times.size()==0||timing>msg_times.get(msg_times.size()-1)) {
				msg_times.add(timing);
				msg_texts.add(text);
				continue;
			}else {
				for(int i=0;i<msg_times.size();i++) {
					if(timing<msg_times.get(i)) {
						msg_times.add(i,timing);
						msg_texts.add(i,text);
						break;
					}
				}
			}
		}
	}
	public void send_msg(String text) {
		ByteBuffer buf = ByteBuffer.allocate(1+text.length());
		buf.put(CMD_WRITE_MSG);
		buf.put(text.getBytes());
		con.send(buf.array());
	}
	public String pop_msg() {
		update();
		for(int i=index;i<msg_times.size();i++) {
			if(msg_times.get(i)>ls_time) {
				index = i;
				ls_time = msg_times.get(i);
				return msg_texts.get(i);
			}
		}
		return null;
	}
	public void seek(long time) {
		ls_time = time;
		index = 0;
	}
	public void print_new() {
		String text;
		while((text=pop_msg())!=null) {
			System.out.println(text);
		}
	}
	/*public static void main(String[] aefsdf) {
		// test program
		MessagingClient client =  new MessagingClient(UplinkManager.easyConnect(),0x9C0010,"Test Bot");
		System.out.println("Connected!");
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e1) {
			e1.printStackTrace();
		}
		client.seek(0);
		while(true) {
			client.print_new();
			try {
				Thread.sleep(100);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}*/
}