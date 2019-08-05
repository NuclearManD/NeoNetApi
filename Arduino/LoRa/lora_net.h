#define LORA_CMD_GET_FREE_ADR 0x55
#define LORA_CMD_DOAI 0x25    // device out access point in
#define LORA_CMD_DIAO 0x82    // device in access point out

uint32_t sender;
int len;
uint32_t port;
byte in_buffer[256];

byte our_adr = 2;
int getPacket(int timeout = -1){
  long timer = millis()+timeout;
  while(timeout==-1||timer>millis()){
    int packetSize = LoRa.parsePacket();
    if (packetSize>=14) {
      
      if(LoRa.read()!=LORA_CMD_DIAO)continue;
      byte target = LoRa.read();
      sender = 0;
      for(int i=0;i<8;i++){
        sender |= ((uint32_t)LoRa.read())<<(i*8);
      }
      port = 0;
      for(int i=0;i<4;i++){
        port |= ((uint32_t)LoRa.read())<<(i*8);
      }
      for(int i=0;i<packetSize-14;i++){
        in_buffer[i] = LoRa.read();
      }
      if(target==our_adr)return packetSize-14;
    }else if(packetSize==1){
      int cmd = LoRa.read();
    }
  }
  return -1;
}

void sendPacket(uint32_t target, byte* data, int len, uint32_t port){
  LoRa.beginPacket();
  LoRa.write(LORA_CMD_DOAI);
  LoRa.write(our_adr);
  for(int i=0;i<8;i++){
    LoRa.write((target>>(8*i))&255);
  }
  for(int i=0;i<4;i++){
    LoRa.write((port>>(8*i))&255);
  }
  LoRa.write(data,len);
  LoRa.endPacket();
}
