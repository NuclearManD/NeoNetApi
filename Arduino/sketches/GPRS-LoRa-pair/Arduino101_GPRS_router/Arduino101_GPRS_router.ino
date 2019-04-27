#include <SPI.h>
#include <LoRa.h>
#include "GPRS.h"
#include "neonet.h"
#include "local.h"

long statusTimer;

void setup() {
  Serial.begin(115200);
  while(!Serial);
  Serial.println("Starting LoRa...");
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("Running GPRS setup...");
  if(setup_gprs()){
    Serial.println("Setup complete");
    Serial.println("My IP address: "+my_ip);
    connect_neonet();
  }else{
    Serial.println("Failed to connect.");
  }
  statusTimer = millis()+15*60*1000;
}

boolean wasClosed = false;

void loop() {
  // check the status timer
  if(statusTimer<millis()){
    Serial.println("Checking status...");
    int q = ping();
    Serial.print("Ping: ");
    Serial.println(q);
    if(!connected){
      Serial.println("Error: no longer connected!");
    }
    statusTimer = millis()+1000*60*15;
  }
  // if we aren't connected then reconnect
  if(!connected){
    Serial.println("Reconnecting to NeoNet...");
    tcp_close();
    connect_neonet();
  }
  // first handle neonet/GPRS network end
  int len = getNrlPacket(100);
  if(len!=-1){
    if((target>>16)==area_code){
      if(nrl_adr!=target){
        // forward packet to local network
        sendLocalPacket(target, nrl_data, len, port, sender);
      }else{
        // the packet is for us!
        handlePacket(len);
      }
    }else{
      // drop packet - cannot forward like this.
      Serial.print("Got illegal forward request from ");
      Serial.print(sender, HEX);
      Serial.print(", target is ");
      Serial.println(target, HEX);
    }
  }
  // now handle local network end
  len = getLocalPacket(100);
  if(len!=-1){
    if((target>>16)==area_code){
      if(nrl_adr!=target){
        // forward packet to local network
        sendLocalPacket(target, nrl_data, len, port, sender);
      }else{
        // the packet is for us!
        handlePacket(len);
      }
    }else{
      // forward packet to neonet
      sendNrlPacket(target, nrl_data, len, port, sender);
    }
  }
}

void handlePacket(int len){
  // here is where the server code can be found
  Serial.print("Got: ");
  Serial.print(target, HEX);
  Serial.write(':');
  Serial.print(port);
  Serial.write(' ');
  Serial.write(nrl_data, len);
  Serial.println();
}


void connect_neonet(){
  if(0==connect_tcp("68.5.129.54",1155)){
    int q = ping();
    Serial.print("Ping: ");
    Serial.println(q);
    Serial.print("Broadcasting address = 0x");
    Serial.println(nrl_adr,HEX);
    byte buf[6];
    for(int i=5;i>=0;i--){
      buf[i]=(area_code>>(8*i))&255;
    }
    sendPacket(CMD_TX, buf, 6);
  }
}
