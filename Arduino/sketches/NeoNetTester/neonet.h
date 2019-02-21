// Assumes use of ESP32
#define CMD_NOP 10
#define CMD_PING 11
#define CMD_PING_ACK 12
#define CMD_TX 13
#define CMD_RQRETX 14

char* neonet_server_ip = "68.5.129.54";
int neonet_server_port = 1155;

uint64_t nrl_adr = 0xC40015;

WiFiClient neonet_socket;


byte in_buffer[65535];

void sendPacket(byte cmd, byte* data, uint16_t len){
  neonet_socket.write(cmd);
  neonet_socket.write(len&255);
  neonet_socket.write(len>>8);
  uint32_t hash = 0xC59638FD^cmd;
  for(int i=0;i<len;i++){
    neonet_socket.write(data[i]);
    uint32_t a = hash^(data[i]<<1);
    a+=(data[i]<<16);
    hash = a^(hash<<3);
    if(0==(i&127))
      delayMicroseconds(66); // don't send it *too* fast
  }
  neonet_socket.write(hash&255);
  neonet_socket.write((hash>>8)&255);
  neonet_socket.write((hash>>16)&255);
  neonet_socket.write((hash>>24)&255);
}


// waits for data, returns length (-1 if timeout)
// timeout is in milliseconds
// buffer should be at least 65535 bytes.
int getData(int timeout, byte* buffer){
  long timer = timeout + millis();

  while(timer>millis()){
    if(neonet_socket.available()>6){
      long packet_timeout = millis()+1000;
      uint8_t  cmd = neonet_socket.read();
      if((cmd>15)||(cmd<10))continue; // wait for a valid packet start
      uint16_t len = neonet_socket.read();
      len|= ((uint16_t)neonet_socket.read()<<8);
      uint16_t idx = 0;
      uint32_t hash = 0xC59638FD^cmd;
      byte b;
      int i;
      while(idx<len){
        for(i=neonet_socket.available();i&&(idx<len);i--){
          b = buffer[idx] = neonet_socket.read();
          hash = ((hash^(b<<1)) + (b<<16))^(hash<<3);
          if((idx&511)==0)
            packet_timeout = millis()+1000;
          idx++;
        }
        if(packet_timeout<millis())goto retx;
      }
      while(neonet_socket.available()<4){
        yield();
        if(packet_timeout<millis())goto retx;
      }
      hash^=neonet_socket.read();
      hash^=(uint32_t)neonet_socket.read()<<8;
      hash^=(uint32_t)neonet_socket.read()<<16;
      hash^=(uint32_t)neonet_socket.read()<<24;
      if(hash){
        // hash does not match
        Serial.println("Detected bad hash.");
        goto clean;
        retx:
        Serial.print("Incoming packet stopped at ");
        Serial.print(idx);
        Serial.print(" of ");
        Serial.print(len);
        Serial.println(" bytes, and timed out.");
        clean:
        Serial.println("Cleaning buffers...");
        while(neonet_socket.available())neonet_socket.read();
        sendPacket(CMD_RQRETX, NULL, 0);
      }else{
        // parse packet here
        if(cmd==CMD_TX){
          // this is what we're looking for
          return len;
        }else if(cmd==CMD_PING){
          // getting a ping
          sendPacket(CMD_PING_ACK, NULL, 0);
        }else if(cmd==CMD_RQRETX){
          // Resend last sent packet
          //resendPacket();
        }else if(cmd==CMD_PING_ACK){
          // ok... then?
        }else if(cmd==CMD_NOP){
          // doing nothing...
        }else{
          // Error: not even the right protocol bruh, like wtf
          // how does i respund to dis?
        }
      }
    }
    yield();
  }
  return -1;
}

long ping(long timeout){
  long time = millis();
  sendPacket(CMD_PING, NULL, 0);
  long timer = timeout + millis();

  while(timer>millis()){
    if(neonet_socket.available()>6){
      long packet_timeout = millis()+1000;
      uint8_t  cmd = neonet_socket.read();
      if((cmd>15)||(cmd<10))continue; // wait for a valid packet start
      uint16_t len = neonet_socket.read();
      len|= (neonet_socket.read()<<8);
      uint16_t idx = 0;
      uint32_t hash = 0xC59638FD^cmd;
      while(idx<len){
        while(neonet_socket.available()&&(idx<len)){
          byte b = in_buffer[idx] = neonet_socket.read();
          uint32_t a = hash^(b<<1);
          a+=(b<<16);
          hash = a^(hash<<3);
          if((idx&127)==0)
            packet_timeout = millis()+1000;
          idx++;
        }
        yield();
        if(packet_timeout<millis())goto retx;
      }
      while(neonet_socket.available()<4){
        yield();
        if(packet_timeout<millis())goto retx;
      }
      hash^=neonet_socket.read();
      hash^=neonet_socket.read()<<8;
      hash^=neonet_socket.read()<<16;
      hash^=neonet_socket.read()<<24;
      if(hash){
        // hash does not match
        Serial.println("Detected bad hash.");
        goto clean;
        retx:
        Serial.print("Incoming packet stopped at ");
        Serial.print(idx);
        Serial.print(" of ");
        Serial.print(len);
        Serial.println(" bytes, and timed out.");
        clean:
        Serial.println("Cleaning buffers...");
        while(neonet_socket.available())neonet_socket.read();
        sendPacket(CMD_RQRETX, NULL, 0);
      }else{
        // parse packet here
        if(cmd==CMD_TX){
          // this will be dropped... request retransmission.
          sendPacket(CMD_RQRETX, NULL, 0);
        }else if(cmd==CMD_PING){
          // getting a ping
          sendPacket(CMD_PING_ACK, NULL, 0);
        }else if(cmd==CMD_RQRETX){
          // Resend last sent packet
          //resendPacket(); // not supported in this release
        }else if(cmd==CMD_PING_ACK){
          // Bang! they responded!
          return millis()-time;
        }else if(cmd==CMD_NOP){
          // doing nothing...
        }else{
          // Error: not even the right protocol bruh, like wtf
          // how does i respund to dis?
        }
      }
    }
    yield();
  }
  return -1;
}

long ping(){
  return ping(4000);
}

void NeoNetSetup(){
  if(neonet_socket.connect(neonet_server_ip,neonet_server_port)){
    byte top[6];
    top[0] = (byte)(nrl_adr>>16);
    top[1] = (byte)(nrl_adr>>24);
    top[2] = (byte)(nrl_adr>>32);
    top[3] = (byte)(nrl_adr>>40);
    top[4] = (byte)(nrl_adr>>48);
    top[5] = (byte)(nrl_adr>>56);
    sendPacket(CMD_TX, top, 6);
    if(ping()==-1)
      Serial.println("Ping failed!");
  }else
    Serial.println("TCP Connection refused!");
}

uint64_t sender;
uint32_t port;
byte* nrl_data;

int getNrlPacket(int timeout){
  int l = getData(timeout, in_buffer);
  if(l<20)return -1;
  uint64_t target = 0;
  for(int i=7;i>=0;i--){
    target = in_buffer[i]|(target<<8);
  }
  if(target==nrl_adr){
    for(int i=15;i>=8;i--){
      sender = in_buffer[i]|(sender<<8);
    }
    for(int i=19;i>=16;i--){
      port = in_buffer[i]|(port<<8);
    }
    nrl_data = in_buffer+20;
    return l-20;
  }
  return -1;
}
