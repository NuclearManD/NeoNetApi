# NeoNetApi
NeoNet API in Python, Java, and Arduino

NeoNet is a network protocol I use that is simple and reliable.  It can be built on any stream, so it makes there be no
difference between an Arduino's serial port and a TCP socket.

Later I will implement routing and connections that will allow large networks to exist over anything from LoRa to TCP - and
a mixture thereof.

Connections NeoNet should be able to be (easily) built upon:
 * TCP
 * Serial Ports
 * Bluetooth?
 * GPRS
 * More, I'm sure...

## Pros/cons of NeoNet

### Pros
 * Can operate over any stream
 * Can work with or without internet connection depending on configuration
 * No routers/NAT: all ports open and servers don't need port forwarding
 * A server running over a TCP uplink can change it's IP and reconnect - and everything still works.
 * Simple, packet-based protocol for sending chunks of data
 * up to 2^64 addresses, and up to 2^32 ports (never will run out in forseeable future)
 * Should be fairly lightweight

### Cons
 * Pretty much zero security
 * Packet reception not garunteed if stream does not garuntee successful reception
 * Probably has certain inefficiencies that a different protocol could address
 * No concept of a connection until the user level, only data transfer

## Languages/Platforms supported
 * Java
 * Python 3
 * ESP32 Arduino (support currently very limited)

## Protocols on NeoNet NRL/NTL
 * Messaging
 * Some otehr random obscure other protocols I made...
 * ... including one for GPS trackers
## Communicated successfully on...
 * Over TCP sockets
 * Over LoRa
 * On SIM900 GPRS shield with Hologram SIM card
 * Over Serial
