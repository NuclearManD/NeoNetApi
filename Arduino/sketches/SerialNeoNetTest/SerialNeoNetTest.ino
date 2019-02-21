HardwareSerial Uplink(2);

#define UPLINK_SPEED 2000000
#define LINKRX 21
#define LINKTX 22

#define CMD_NOP 10
#define CMD_PING 11
#define CMD_PING_ACK 12
#define CMD_TX 13
#define CMD_RQRETX 14

#define null NULL

byte buffer[65535];

void setup() {
  Serial.begin(230400);
  Serial.print("Link speed: ");
  Serial.println(UPLINK_SPEED);
  Serial.println("Establishing uplink...");
  Uplink.begin(UPLINK_SPEED, SERIAL_8N1, LINKRX, LINKTX);
  if(connect()){
    Serial.println("Connection established.  Running tests...");
    Serial.println("1. Testing ping:");
    long ping_ = ping();
    Serial.print("Ping was ");
    Serial.print(ping_);
    Serial.println("ms.");
    Serial.println("2. Testing connection speed, sending 1MB of data in 8192x128 byte packets:");
    long time = millis();
    int strikes = 0;
    for(int i=0;i<8192;i++){
      sendPacket(CMD_TX, buffer, 128);
      int r=getData(4000, buffer);
      if(r==-1){
        if(strikes>=10)goto failed;
        strikes++;
        Serial.print("Error #");
        Serial.print(strikes);
        Serial.println(" of 10");
        Serial.print("So far ");
        Serial.print(i);
        Serial.println(" packets were sent sucessfully.");
        i--;
      }
      if((i&127)==127){
        Serial.print("Sent ");
        Serial.print(i+1);
        Serial.println(" of 8192 packets.");
      }
    }
    time=millis()-time;
    Serial.print("Connection speed: ");
    Serial.print(8000.0/time);
    Serial.println(" Mbps");
    Serial.println("3. Testing connection speed, sending 1MB of data in 128x8192 byte packets:");
    time = millis();
    strikes = 0;
    for(int i=0;i<128;i++){
      sendPacket(CMD_TX, buffer, 8192);
      int r=getData(8000, buffer);
      if(r==-1){
        if(strikes>=10)goto failed;
        strikes++;
        Serial.print("Error #");
        Serial.print(strikes);
        Serial.println(" of 10");
        Serial.print("So far ");
        Serial.print(i);
        Serial.println(" packets were sent sucessfully.");
        i--;
      }
    }
    time=millis()-time;
    Serial.print("Connection speed: ");
    Serial.print(8000.0/time);
    Serial.println(" Mbps");
    Serial.println("4. Testing connection speed, sending 1MB of data in 32x32768 byte packets:");
    time = millis();
    strikes = 0;
    for(int i=0;i<32;i++){
      sendPacket(CMD_TX, buffer, 32768);
      int r=getData(8000, buffer);
      if(r==-1){
        if(strikes>=10)goto failed;
        strikes++;
        Serial.print("Error #");
        Serial.print(strikes);
        Serial.println(" of 10");
        Serial.print("So far ");
        Serial.print(i);
        Serial.println(" packets were sent sucessfully.");
        i--;
      }
    }
    time=millis()-time;
    Serial.print("Connection speed: ");
    Serial.print(8000.0/time);
    Serial.println(" Mbps");
    goto ok_lbl;
    failed:
    Serial.println("Error: test failed.");
    ok_lbl:
    ;
  }else{
    Serial.println("There's nobody on the other end!  Waiting for a connection.");
  }
  Serial.println("Starting test server...");
}
long debugtimer = 0;
void loop() {
  int len = getData(10000, buffer);
  if(len>0){
    if(debugtimer<millis()){
      Serial.print("Data of length ");
      Serial.print(len);
      Serial.println(" has been received.");
      if(len<32){
        Serial.print("Contents: ");
        Serial.println((char*)buffer);
      }
    }
    String result = "Rcvd ";
    result+=String(len)+";";
    sendPacket(CMD_TX, (byte*)result.c_str(), result.length());
    if(debugtimer<millis()){
      Serial.print("Returned ");
      Serial.println(result);
      debugtimer = millis()+300;
    }
  }else if(len==0){
    Serial.println("Received empty packet...");
  }
}
byte lscmd;
byte* lsdata;
uint16_t lslen;

void sendPacket(byte cmd, byte* data, uint16_t len){
  if(cmd!=CMD_RQRETX){
    lscmd = cmd;
    lsdata = data;
    lslen = len;
  }
  Uplink.write(cmd);
  Uplink.write(len&255);
  Uplink.write(((uint16_t)len>>8)&255);
  uint32_t hash = 0xC59638FD^cmd;
  for(int i=0;i<len;i++){
    Uplink.write(data[i]);
    uint32_t a = hash^(data[i]<<1);
    a+=(data[i]<<16);
    hash = a^(hash<<3);
    if(0==(i&127))
      delayMicroseconds(66); // don't send it *too* fast
  }
  Uplink.write(hash&255);
  Uplink.write((hash>>8)&255);
  Uplink.write((hash>>16)&255);
  Uplink.write((hash>>24)&255);
}

void resendPacket(){
  sendPacket(lscmd,lsdata,lslen);
}

// waits for data, returns length (-1 if timeout)
// timeout is in milliseconds
// buffer should be at least 65535 bytes.
int getData(int timeout, byte* buffer){
  long timer = timeout + millis();

  while(timer>millis()){
    if(Uplink.available()>6){
      long packet_timeout = millis()+1000;
      uint8_t  cmd = Uplink.read();
      if((cmd>15)||(cmd<10))continue; // wait for a valid packet start
      uint16_t len = Uplink.read();
      len|= ((uint16_t)Uplink.read()<<8);
      uint16_t idx = 0;
      uint32_t hash = 0xC59638FD^cmd;
      byte b;
      int i;
      while(idx<len){
        for(i=Uplink.available();i&&(idx<len);i--){
          b = buffer[idx] = Uplink.read();
          hash = ((hash^(b<<1)) + (b<<16))^(hash<<3);
          if((idx&511)==0)
            packet_timeout = millis()+1000;
          idx++;
        }
        if(packet_timeout<millis())goto retx;
      }
      while(Uplink.available()<4){
        yield();
        if(packet_timeout<millis())goto retx;
      }
      hash^=Uplink.read();
      hash^=(uint32_t)Uplink.read()<<8;
      hash^=(uint32_t)Uplink.read()<<16;
      hash^=(uint32_t)Uplink.read()<<24;
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
        while(Uplink.available())Uplink.read();
        sendPacket(CMD_RQRETX, null, 0);
      }else{
        // parse packet here
        if(cmd==CMD_TX){
          // this is what we're looking for
          return len;
        }else if(cmd==CMD_PING){
          // getting a ping
          Serial.println("Ping received.");
          sendPacket(CMD_PING_ACK, null, 0);
        }else if(cmd==CMD_RQRETX){
          // Resend last sent packet
          resendPacket();
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
  sendPacket(CMD_PING, null, 0);
  long timer = timeout + millis();

  while(timer>millis()){
    if(Uplink.available()>6){
      long packet_timeout = millis()+1000;
      uint8_t  cmd = Uplink.read();
      if((cmd>15)||(cmd<10))continue; // wait for a valid packet start
      uint16_t len = Uplink.read();
      len|= (Uplink.read()<<8);
      uint16_t idx = 0;
      uint32_t hash = 0xC59638FD^cmd;
      while(idx<len){
        while(Uplink.available()&&(idx<len)){
          byte b = buffer[idx] = Uplink.read();
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
      while(Uplink.available()<4){
        yield();
        if(packet_timeout<millis())goto retx;
      }
      hash^=Uplink.read();
      hash^=Uplink.read()<<8;
      hash^=Uplink.read()<<16;
      hash^=Uplink.read()<<24;
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
        while(Uplink.available())Uplink.read();
        sendPacket(CMD_RQRETX, null, 0);
      }else{
        // parse packet here
        if(cmd==CMD_TX){
          // this will be dropped... request retransmission.
          sendPacket(CMD_RQRETX, null, 0);
        }else if(cmd==CMD_PING){
          // getting a ping
          Serial.println("Ping received.");
          sendPacket(CMD_PING_ACK, null, 0);
        }else if(cmd==CMD_RQRETX){
          // Resend last sent packet
          resendPacket();
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

boolean connect(){
  Serial.println("Sending connection ping(s)...");
  for(int i=0;i<4;i++){
    if(ping(3000)==-1){
      Serial.print("Ping #");
      Serial.print(i);
      Serial.println(" of 4 failed.");
    }else return true;
  }
  return false;
}
