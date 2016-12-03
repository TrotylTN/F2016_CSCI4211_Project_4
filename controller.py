

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet

h1_IP = IPAddr('10.0.0.1')
print dir(h1_IP), h1_IP.toUnsignedN()
h1_MAC = EthAddr('00:00:00:00:00:01')

h2_IP = IPAddr('10.0.0.2')
h2_MAC = EthAddr('00:00:00:00:00:02')

h3_IP = IPAddr('10.0.0.3')
h3_MAC = EthAddr('00:00:00:00:00:03')

h4_IP = IPAddr('10.0.0.4')
h4_MAC = EthAddr('00:00:00:00:00:04')

h5_IP = IPAddr('10.0.0.5')
h5_MAC = EthAddr('00:00:00:00:00:05')

h6_IP = IPAddr('10.0.0.6')
h6_MAC = EthAddr('00:00:00:00:00:06')

print "OK...."

ARP_table = {}
ARP_table[h1_IP] = h1_MAC
ARP_table[h2_IP] = h2_MAC
ARP_table[h3_IP] = h3_MAC
ARP_table[h4_IP] = h4_MAC
ARP_table[h5_IP] = h5_MAC
ARP_table[h6_IP] = h6_MAC

def _handle_ARP_request(packet):
  src_MAC = packet.payload.hwsrc
  src_IP = packet.payload.protosrc
  dst_MAC = packet.payload.hwdst
  dst_IP = packet.payload.protodst
  print src_IP, "ASK" , dst_IP, "Old dst", dst_MAC 
  dst_MAC = ARP_table[dst_IP]
  print "New mac", dst_MAC
  r = arp()
  #r.hwtype = r.HW_TYPE_ETHERNET
  #r.prototype = r.PROTO_TYPE_IP
  #r.hwlen = 6
  #r.protolen = r.protolen
  r.opcode = arp.REPLY
  r.hwdst = src_MAC
  r.protodst = src_IP
  r.hwsrc = dst_MAC
  r.protosrc = dst_IP
  e = ethernet(type=ethernet.ARP_TYPE, src=dst_MAC, dst=src_MAC)
  e.set_payload(r)
  return e
  
	
  
def _handle_PacketIn (event):
 
  packet = event.parsed

  #'dump', 'err', 'find', 'hdr', 'hwdst', 'hwlen', 'hwsrc', 'hwtype', 'msg', 'next', 'opcode', 'pack', 'parse', 'parsed', 'payload', 'pre_hdr', 'prev', 'protodst', 'protolen', 'protosrc', 'prototype', 'raw', 'set_payload', 'unpack', 'warn']

  if isinstance(packet.payload, arp):
    print "GET ARP request"
    e = _handle_ARP_request(packet)
    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
    msg.in_port = event.port
    event.connection.send(msg)
    
  elif isinstance(packet.next, ipv4):
    print "ipv4"


def launch (disable_flood = False):
  global all_ports
  if disable_flood:
    all_ports = of.OFPP_ALL

  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  #log.info("Pair-Learning switch running.")
  




