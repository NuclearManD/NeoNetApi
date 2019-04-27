#define LORA_CMD_GET_FREE_ADR 0x55
#define LORA_CMD_DOAI 0x25    // device out access point in
#define LORA_CMD_DIAO 0x82    // device in access point out

byte next_address = 2;
int getLocalPacket(int timeout = -1){
  long timer = millis()+timeout;
  while(timeout==-1||timer>millis()){
    int packetSize = LoRa.parsePacket();
    if (packetSize>=13) {
      sender = (area_code<<16) | LoRa.read();
      for(int i=0;i<8;i++){
        target = LoRa.read()|(target<<8);
      }
      for(int i=0;i<4;i++){
        port = LoRa.read()|(port<<8);
      }
      for(int i=0;i<packetSize-13;i++){
        in_buffer[i] = LoRa.read();
      }
      nrl_data = in_buffer;
      return packetSize-13;
    }else if(packetSize==1){
      int cmd = LoRa.read();
    }
  }
  return -1;
}

void sendLocalPacket(uint16_t target, byte* data, int len, uint32_t port, uint64_t sender=nrl_adr){
  LoRa.beginPacket();
  LoRa.write(target&255);
  for(int i=0;i<8;i++){
    LoRa.write((sender>>i)&255);
  }
  for(int i=0;i<4;i++){
    LoRa.write((port>>i)&255);
  }
  LoRa.write(data,len);
  LoRa.endPacket();
}
