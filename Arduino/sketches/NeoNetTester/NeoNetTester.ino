// Playing a digital WAV recording repeatadly using the XTronical DAC Audio library
// prints out to the serial monitor numbers counting up showing that the sound plays 
// independently of the main loop
// See www.xtronical.com for write ups on sound, the hardware required and how to make
// the wav files and include them in your code

#include <WiFi.h>
#include "neonet.h"

void setup() {
  
  Serial.begin(115200);
  WiFi.begin("nti","littleguys");
  
  while (WiFi.status() != WL_CONNECTED) {
    yield();
  }
  Serial.println("We're online!");

  NeoNetSetup();
}

int l;

void loop(){
  if((l=getNrlPacket(8000))!=-1){
    Serial.write(nrl_data, l);
    Serial.println();
  }
}
