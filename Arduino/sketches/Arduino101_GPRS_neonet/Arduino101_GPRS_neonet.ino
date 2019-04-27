#include "GPRS.h"
#include "neonet.h"

void setup() {
  Serial.begin(115200);
  while(!Serial);
  Serial.println("Running GPRS setup...");
  if(setup_gprs()){
    Serial.println("Setup complete");
    Serial.println("My IP address: "+my_ip);
    if(0==connect_tcp("68.5.129.54",1155)){
      //delay(500);
      //tcp_send("HELLO");
      //delay(10000);
      //tcp_close();
      for(int i=0;i<4;i++){
        int q = ping();
        Serial.print("Ping: ");
        Serial.println(q);
        if(!connected)break;
        //loop();
      }//*/
      tcp_close();
    }
  }else{
    Serial.println("Failed to connect.");
  }
}

boolean wasClosed = false;

void loop() {
  /*gprsClean();
  if(wasClosed==connected){
    wasClosed=true;
    Serial.println("Connection closed.");
  }
  while(tcp_available()){
    Serial.print(tcp_read(), HEX);
    Serial.write(' ');
  }*/
  while(Serial.available()){
    GPRS.write(Serial.read());
  }
  while(GPRS.available()){
    Serial.write(GPRS.read());
  }
}
