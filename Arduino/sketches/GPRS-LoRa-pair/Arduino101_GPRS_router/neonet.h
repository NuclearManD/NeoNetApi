// Assumes use of ESP32
#define CMD_NOP 10
#define CMD_PING 11
#define CMD_PING_ACK 12
#define CMD_TX 13
#define CMD_RQRETX 14

//#define NEONET_DEBUG

uint64_t nrl_adr = 0x10820001; // end with '0001' for gateway (this is a router)
uint64_t area_code = nrl_adr>>16;

byte in_buffer[512];
byte out_buffer[512];

void sendPacket(byte cmd, byte* data, uint16_t len){
  #ifdef NEONET_DEBUG
  Serial.print("Sending NeoNet packet, cmd=");
  Serial.println(cmd);
  Serial.print("\tlen=");
  Serial.println(len);
  #endif
  out_buffer[0]=cmd;
  out_buffer[1]=len&255;
  out_buffer[2]=len>>8;
  uint32_t hash = 0xC59638FD^cmd;
  for(int i=0;i<len;i++){
    out_buffer[i+3]=data[i];
    uint32_t a = hash^(data[i]<<1);
    a+=(data[i]<<16);
    hash = a^(hash<<3);
  }
  out_buffer[len+3]=hash&255;
  out_buffer[len+4]=(hash>>8)&255;
  out_buffer[len+5]=(hash>>16)&255;
  out_buffer[len+6]=(hash>>24)&255;
  for(int i=0;i<10;i++){
    #ifdef NEONET_DEBUG
    Serial.print("\tPacket send try #");
    Serial.println(i+1);
    #endif
    if(!connected)break;
    if(tcp_send(out_buffer, len+7)==0)return;
  }
  #ifdef NEONET_DEBUG
  Serial.println("\tFailed to send the packet!");
  #endif
}

byte packet_cmd = -1;
int packet_len = 0;
boolean getPacketNow(){
  if(!connected)return false;
  long timer = millis();
  sys_yield(); // read buffers, etc
  if(tcp_available()>6){
    long packet_timeout = millis()+1000;
    uint8_t  cmd = tcp_read();
    if((cmd>15)||(cmd<10))return false; // wait for a valid packet start
    uint16_t len = tcp_read();
    len|= ((uint16_t)tcp_read()<<8);
    uint16_t idx = 0;
    uint32_t hash = 0xC59638FD^cmd;
    byte b;
    int i;
    #ifdef NEONET_DEBUG
    Serial.print("Got NeoNet packet, cmd=");
    Serial.println(cmd);
    Serial.print("\tlen=");
    Serial.println(len);
    #endif
    while(idx<len){
      sys_yield();
      for(i=tcp_available();i&&(idx<len);i--){
        b = in_buffer[idx] = tcp_read();
        hash = ((hash^(b<<1)) + (b<<16))^(hash<<3);
        if((idx&511)==0)
          packet_timeout = millis()+1000;
        idx++;
      }
      if(packet_timeout<millis())goto retx;
    }
    while(tcp_available()<4){
      sys_yield();
      if(packet_timeout<millis())goto retx;
    }
    hash^=tcp_read();
    hash^=(uint32_t)tcp_read()<<8;
    hash^=(uint32_t)tcp_read()<<16;
    hash^=(uint32_t)tcp_read()<<24;
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
      while(tcp_available())tcp_read();
      sendPacket(CMD_RQRETX, NULL, 0);
    }else{
      packet_cmd = cmd;
      packet_len = len;
      #ifdef NEONET_DEBUG
      Serial.print("Took ");
      Serial.print(millis()-timer);
      Serial.println("ms to read that packet.");
      #endif
      return true;
    }
  }
  #ifdef NEONET_DEBUG
  else if(tcp_available()){
    Serial.print(tcp_available());
    Serial.println(" is not enough bytes for a NeoNet packet.");
  }
  #endif
  return false;
}


// waits for data, returns length (-1 if timeout)
// timeout is in milliseconds
int getData(int timeout, byte* buffer){
  if(!connected)return -1;
  long timer = timeout + millis();

  while(timer>millis()){
    while(getPacketNow()){
      byte cmd = packet_cmd;
      // parse packet here
      if(cmd==CMD_TX){
        // this is what we're looking for
        return packet_len;
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
    if(!connected)return -1;
    //sys_yield();
  }
  return -1;
}

long ping(long timeout){
  if(!connected)return -1;
  long time = millis();
  sendPacket(CMD_PING, NULL, 0);
  long timer = timeout + millis();

  //sys_yield();

  while(timer>millis()){
    while(getPacketNow()){
      byte cmd = packet_cmd;
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
    //sys_yield();
    if(!connected)return -1;
  }
  return -1;
}

long ping(){
  return ping(8000);
}

uint64_t sender;
uint32_t port;
uint64_t target;
byte* nrl_data;

int getNrlPacket(int timeout){
  int l = getData(timeout, in_buffer);
  if(l<20)return -1;
  for(int i=7;i>=0;i--){
    target = in_buffer[i]|(target<<8);
  }
  for(int i=15;i>=8;i--){
    sender = in_buffer[i]|(sender<<8);
  }
  for(int i=19;i>=16;i--){
    port = in_buffer[i]|(port<<8);
  }
  nrl_data = in_buffer+20;
  return l-20;
}

void sendNrlPacket(uint64_t target, byte* data, int len, uint32_t port, uint64_t sender=nrl_adr){
  byte buffer[len+20];
  for(int i=7;i>=0;i--){
    buffer[i]=(target>>(8*i))&255;
  }
  for(int i=15;i>=8;i--){
    buffer[i]=(sender>>(8*(i-8)))&255;
  }
  for(int i=19;i>=16;i--){
    buffer[i]=(port>>(8*(i-16)))&255;
  }
  for(int i=0;i<len;i++){
    buffer[i+20]=data[i];
  }
  sendPacket(CMD_TX, buffer, len+20);
}
