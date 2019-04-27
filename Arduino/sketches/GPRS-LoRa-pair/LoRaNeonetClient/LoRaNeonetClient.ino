#include <SPI.h>
#include <LoRa.h>
#include "lora_net.h"

void setup() {
  Serial.begin(115200);
  while(!Serial);
  Serial.println("Starting LoRa...");
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("Success!");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.write(in_buffer,getPacket());
  Serial.println();
}
