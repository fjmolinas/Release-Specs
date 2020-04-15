## Goal: Check single-hop ICMP connectivity over IPv6

Task #01 - ICMPv6 link-local echo with iotlab-m3
================================================
### Description

ICMPv6 echo request/reply exchange between two iotlab-m3 nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               20ms
* Payload:                0B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #02 - ICMPv6 multicast echo with iotlab-m3/samr21-xpro
===========================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #03 - ICMPv6 echo with large payload
=========================================
### Description

ICMPv6 echo request/reply exchange between two nodes.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  500
* Interval:               300ms
* Payload:                1kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).

Task #04 - ICMPv6 echo with iotlab-m3/samr21-xpro 15 minutes
============================================================
### Description

ICMPv6 echo request/reply exchange between an iotlab-m3 and a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  10000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #05 (Experimental) - ICMPv6 multicast echo with samr21-xpro/remote
=======================================================================
### Description

ICMPv6 echo request/reply exchange between  a Zolertia Remote node (CC2538) and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #06 (Experimental) - ICMPv6 link-local echo with samr21-xpro/remote
========================================================================
### Description

ICMPv6 echo request/reply exchange between a Zolertia Remote node (CC2538) and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               100ms
* Payload:                50B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #07 (Experimental) - ICMPv6 multicast echo with samr21-xpro/zero + xbee
============================================================================
### Description

ICMPv6 echo request/reply exchange between an Arduino Zero + XBee node and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                17
* Count:                  1000
* Interval:               150ms
* Payload:                50B
* Destination Address:    ff02::1

### Result

<10% packets lost on the pinging node.

Task #08 (Experimental) - ICMPv6 echo with samr21-xpro/zero + xbee
==================================================================
### Description

ICMPv6 echo request/reply exchange between an Arduino Zero + XBee node and
a samr21-xpro node.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  1000
* Interval:               100ms
* Payload:                100B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.

Task #09 - ICMPv6 stress test on iotlab-m3
==========================================
### Description

Rapid ICMPv6 echo request/reply exchange from two iotlab-m3 nodes simultaneously
to one iotlab-m3.
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  200
* Interval:               0ms
* Payload:                1232B
* Destination Address:    Link local unicast (fe80::.../64)

### Result

All nodes are still running, reachable, and the packet buffer is empty 3 seconds
after completions (use module `gnrc_pktbuf_cmd`).
Packet loss is irrelevant in this stress test.

Task #10 (Exprimental) - ICMPv6 echo with large payload (IPv6 fragmentation)
============================================================================
### Description

ICMPv6 echo request/reply exchange between two nodes (make sure module
`gnrc_ipv6_ext_frag` is included and the packet buffer is large enough to handle
both the fragmented and reassembled requests/replies).
* Stack configuration:    6LoWPAN (default)
* Channel:                26
* Count:                  200
* Interval:               600ms
* Payload:                2kB
* Destination Address:    Link local unicast (fe80::.../64)

### Result

<10% packets lost on the pinging node.
No leaks in the packet buffer (check with `gnrc_pktbuf_cmd`).
