#define LORA_CMD_GET_FREE_ADR 0x55
#define LORA_CMD_DOAI 0x25    // device out access point in
#define LORA_CMD_DIAO 0x82    // device in access point out

uint64_t sender;
int len;
uint32_t port;
byte in_buffer[256];

byte our_adr = 2;
int getPacket(int timeout = -1){
  long timer = millis()+timeout;
  while(timeout==-1||timer>millis()){
    int packetSize = LoRa.parsePacket();
    if (packetSize>=13) {
      byte target = LoRa.read();
      for(int i=0;i<8;i++){
        sender = LoRa.read()|(sender<<8);
      }
      for(int i=0;i<4;i++){
        port = LoRa.read()|(port<<8);
      }
      for(int i=0;i<packetSize-13;i++){
        in_buffer[i] = LoRa.read();
      }
      if(target==our_adr)return packetSize-13;
    }else if(packetSize==1){
      int cmd = LoRa.read();
    }
  }
  return -1;
}

void sendPacket(uint16_t target, byte* data, int len, uint32_t port){
  LoRa.beginPacket();
  LoRa.write(our_adr);
  for(int i=0;i<8;i++){
    LoRa.write((target>>i)&255);
  }
  for(int i=0;i<4;i++){
    LoRa.write((port>>i)&255);
  }
  LoRa.write(data,len);
  LoRa.endPacket();
}
