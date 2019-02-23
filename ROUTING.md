## Routing Files

Routing files tell Uplink Managers how to route NRL packets.  They allow easy configuration of routes.

File extension should be '.nnr' for "NeoNet Route file"

### Format

Each line follows the format:
```
route TARGET_IP ROUTED_DEVICE
```
There can also be comments:
```
# this is a comment
; this too
```
A blank line does nothing.
Example file:
~~~~
# block outgoing packets to server 0x7f230105 by sending them to null
route 0x7f230105 null

# forward packets for 0x99C10053 to my Arduino via the serial port
route 0x99C10053 tty0

# forward all other packets to the TCP uplink (tcp0)
route * tcp0
~~~~

The '\*'' means 'default', and all other traffic falls into this category.  A 0x05\*\*01\*\*\*\* would specify that any outgoing or forwarded traffic that matched the given address where there are no asteriks would be routed.

For example, if this was your routing file:
~~~~
route 0x00C7090001 link0
route 0x00C7****** link1
route 0x00******01 link2
route * link3
~~~~

then:
 * packets going to 0xC7090001 would go to link0
 * packets going to 0xC7000002, 0xC7000003, ... 0xC7FFFFFF would go to link1
 * packets going to 0x0010928501, 0x00ff028701, etc would go to link2
 * everything else goes to link3

Note that, depending on the program that reads the file, the in-memory routing table may be altered as new routes are defined or new uplinks are established.  Additionally, if route addresses overlap then the selected route is undefined, and depends on the program, so don't make them overlap.

the `route` word is used as a command because other commands may be added in the future.

### Future of these files

I would like to make them support the forwarding of incoming packets as well, this would be extremely useful.  Also it would be great if they could configure the creation of connections.
