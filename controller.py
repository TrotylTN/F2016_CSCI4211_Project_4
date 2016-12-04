

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet

from pox.lib.revent import *  
from pox.lib.recoco import Timer  
from collections import defaultdict  
from pox.openflow.discovery import Discovery  
from pox.lib.util import dpid_to_str  
import time

h1_IP = IPAddr('10.0.0.1')
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

l1_forwarding = {}
l2_forwarding = {}
l3_forwarding = {}
s4_forwarding = {}
s5_forwarding = {}
# forwarding = [l1_forwarding, l2_forwarding, l3]
# l1_forwarding[(src, dst)] = port

def generate():
  l1_forwarding[(h1_MAC, h2_MAC)] = 4
  l1_forwarding[(h1_MAC, h3_MAC)] = 1
  l1_forwarding[(h1_MAC, h4_MAC)] = 1
  l1_forwarding[(h1_MAC, h5_MAC)] = 1
  l1_forwarding[(h1_MAC, h6_MAC)] = 1

  l1_forwarding[(h2_MAC, h1_MAC)] = 3
  l1_forwarding[(h2_MAC, h3_MAC)] = 2
  l1_forwarding[(h2_MAC, h4_MAC)] = 2
  l1_forwarding[(h2_MAC, h5_MAC)] = 2
  l1_forwarding[(h2_MAC, h6_MAC)] = 2

  l1_forwarding[(h3_MAC, h1_MAC)] = 3
  l1_forwarding[(h4_MAC, h1_MAC)] = 3
  l1_forwarding[(h5_MAC, h1_MAC)] = 3
  l1_forwarding[(h6_MAC, h1_MAC)] = 3

  l1_forwarding[(h3_MAC, h2_MAC)] = 4 
  l1_forwarding[(h4_MAC, h2_MAC)] = 4
  l1_forwarding[(h5_MAC, h2_MAC)] = 4
  l1_forwarding[(h6_MAC, h2_MAC)] = 4
  
  l2_forwarding[(h3_MAC, h1_MAC)] = 1
  l2_forwarding[(h3_MAC, h2_MAC)] = 1
  l2_forwarding[(h3_MAC, h4_MAC)] = 4
  l2_forwarding[(h3_MAC, h5_MAC)] = 1
  l2_forwarding[(h3_MAC, h6_MAC)] = 1

  l2_forwarding[(h4_MAC, h1_MAC)] = 2
  l2_forwarding[(h4_MAC, h2_MAC)] = 2
  l2_forwarding[(h4_MAC, h3_MAC)] = 3
  l2_forwarding[(h4_MAC, h5_MAC)] = 2
  l2_forwarding[(h4_MAC, h6_MAC)] = 2

  l2_forwarding[(h1_MAC, h3_MAC)] = 3
  l2_forwarding[(h2_MAC, h3_MAC)] = 3
  l2_forwarding[(h5_MAC, h3_MAC)] = 3
  l2_forwarding[(h6_MAC, h3_MAC)] = 3

  l2_forwarding[(h1_MAC, h4_MAC)] = 4 
  l2_forwarding[(h2_MAC, h4_MAC)] = 4
  l2_forwarding[(h5_MAC, h4_MAC)] = 4
  l2_forwarding[(h6_MAC, h4_MAC)] = 4

  l3_forwarding[(h5_MAC, h1_MAC)] = 1
  l3_forwarding[(h5_MAC, h2_MAC)] = 1
  l3_forwarding[(h5_MAC, h3_MAC)] = 1
  l3_forwarding[(h5_MAC, h4_MAC)] = 1
  l3_forwarding[(h5_MAC, h6_MAC)] = 4

  l3_forwarding[(h6_MAC, h1_MAC)] = 2
  l3_forwarding[(h6_MAC, h2_MAC)] = 2
  l3_forwarding[(h6_MAC, h3_MAC)] = 2
  l3_forwarding[(h6_MAC, h4_MAC)] = 2
  l3_forwarding[(h6_MAC, h5_MAC)] = 3

  l3_forwarding[(h1_MAC, h5_MAC)] = 3
  l3_forwarding[(h2_MAC, h5_MAC)] = 3
  l3_forwarding[(h3_MAC, h5_MAC)] = 3
  l3_forwarding[(h4_MAC, h5_MAC)] = 3

  l3_forwarding[(h1_MAC, h6_MAC)] = 4 
  l3_forwarding[(h2_MAC, h6_MAC)] = 4
  l3_forwarding[(h3_MAC, h6_MAC)] = 4
  l3_forwarding[(h4_MAC, h6_MAC)] = 4

  s4_forwarding[h1_MAC] = 1
  s4_forwarding[h2_MAC] = 1
  s4_forwarding[h3_MAC] = 2
  s4_forwarding[h4_MAC] = 2
  s4_forwarding[h5_MAC] = 3
  s4_forwarding[h6_MAC] = 3

  s5_forwarding[h1_MAC] = 1
  s5_forwarding[h2_MAC] = 1
  s5_forwarding[h3_MAC] = 2
  s5_forwarding[h4_MAC] = 2
  s5_forwarding[h5_MAC] = 3
  s5_forwarding[h6_MAC] = 3


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
  
def _handle_ConnectionIn(event):
  print("Switch %d connected" % event.dpid)
  if event.dpid == 1:
    print("pid = 1")
    for key in sorted(l1_forwarding):
      msg = of.ofp_flow_mod()
      msg.match.dl_src = key[0]
      msg.match.dl_dst = key[1]
      port = l1_forwarding[key]
      msg.actions.append(of.ofp_action_output(port = port))
      print "add rule 1"
      event.connection.send(msg)
  elif event.dpid == 2:
    for key in sorted(l2_forwarding):
      msg = of.ofp_flow_mod()
      msg.match.dl_src = key[0]
      msg.match.dl_dst = key[1]
      port = l2_forwarding[key]
      msg.actions.append(of.ofp_action_output(port = port))
      print "Add rule 2"
      event.connection.send(msg)
  elif event.dpid == 3:
    for key in sorted(l3_forwarding):
      msg = of.ofp_flow_mod()
      msg.match.dl_src = key[0]
      msg.match.dl_dst = key[1]
      port = l3_forwarding[key]
      msg.actions.append(of.ofp_action_output(port = port))
      event.connection.send(msg)
  elif event.dpid == 4:
    for key in sorted(s4_forwarding):
      msg = of.ofp_flow_mod()
      msg.match.dl_dst = key
      port = s4_forwarding[key]
      msg.actions.append(of.ofp_action_output(port = port))
      event.connection.send(msg)
  elif event.dpid == 5:
    for key in sorted(s5_forwarding):
      msg = of.ofp_flow_mod()
      msg.match.dl_dst = key
      port = s5_forwarding[key]
      msg.actions.append(of.ofp_action_output(port = port))
      event.connection.send(msg)
  else:
    print("Error")

  
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
    
  # elif isinstance(packet.next, ipv4):
  #   print "ipv4", event.dpid

class topoDiscovery(EventMixin):

    def __init__(self):
        def startup():
            core.openflow.addListeners(self, priority = 100)
            core.openflow_discovery.addListeners(self)
        core.call_when_ready(startup, ('openflow','openflow_discovery'))
        print "init over"
    def _handle_LinkEvent(self, event):
        if (event.added):
          return
        l = event.link
        sw1 = l.dpid1
        sw2 = l.dpid2
        pt1 = l.port1
        pt2 = l.port2
        # print dir(event.link.dpid1)

        con1 = core.openflow.getConnection(l.dpid1)
        con2 = core.openflow.getConnection(l.dpid2)
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        con1.send(msg)
        con2.send(msg)
        print("Send OK")

        print 'link added is %s'%event.added
        print 'link removed is %s' %event.removed
        print 'switch1 %d' %l.dpid1
        print 'port1 %d' %l.port1
        print 'switch2 %d' %l.dpid2
        print 'port2 %d' %l.port2

def launch (disable_flood = False):
  global all_ports
  if disable_flood:
    all_ports = of.OFPP_ALL
  generate()
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionIn)
  core.registerNew(topoDiscovery)
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  #log.info("Pair-Learning switch running.")
  




