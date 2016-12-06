from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet

from pox.lib.revent import *  
from pox.lib.recoco import Timer  
from collections import defaultdict  
from pox.openflow.discovery import *
from pox.lib.util import dpid_to_str  
import time

forwardings = [[{}, {}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}, {}]]

ipbase = '10.0.0.'
macbase = '00:00:00:00:00:0'
emptymac = "-1"
priority1 = 100
priority2 = 200
status = 3

ARP_table = {}

link_state = {4:[0, 1, 1, 1],
              5:[0, 1, 1, 1]}

def generate_arp_table():
  for i in range(1, 7):
    ARP_table[IPAddr(ipbase+str(i))] = EthAddr(macbase+str(i))

def generator(status, sid):
    state = [status // 2 != 0, status % 2 != 0]
    if sid in [4, 5]:
        for i in range(1, 7):
            forwardings[status][sid][(emptymac, macbase+str(i))] = ((i + 1) // 2, priority1)
    elif sid in [1, 2, 3]:
        hosts = [sid * 2 - 1, sid * 2]
        for i in range(2):
            if i==0 and not state[i]:
                port = 2
            elif i==1 and not state[i]:
                port = 1
            else:
                port = i + 1
            forwardings[status][sid][(macbase+str(hosts[i]), emptymac)] = (port, priority1)
            forwardings[status][sid][(emptymac, macbase+str(hosts[i]))] = ((i + 3), priority2)

def generate_tables():
  for s in range(1, 4):
    for switch in range(1, 6):
      generator(s, switch)  

def print_status():
  global status
  state = [status // 2 != 0, status % 2 != 0]
  print "Status: S4, S5", state

def _handle_ARP_request(packet):
  src_MAC = packet.payload.hwsrc
  src_IP = packet.payload.protosrc
  dst_MAC = packet.payload.hwdst
  dst_IP = packet.payload.protodst
  print src_IP, "asks for" , dst_IP
  dst_MAC = ARP_table[dst_IP]
  r = arp()
  r.opcode = arp.REPLY
  r.hwdst = src_MAC
  r.protodst = src_IP
  r.hwsrc = dst_MAC
  r.protosrc = dst_IP
  e = ethernet(type=ethernet.ARP_TYPE, src=dst_MAC, dst=src_MAC)
  e.set_payload(r)
  return e

def teach(status, sid):
  k = sorted(forwardings[status][sid].keys())
  con = core.openflow.getConnection(sid)
  for t in k:
    port, priority = forwardings[status][sid][t]
    msg = of.ofp_flow_mod()
    if (t[0] != emptymac):
      msg.match.dl_src = EthAddr(t[0])
    if (t[1] != emptymac):
      msg.match.dl_dst = EthAddr(t[1])
    msg.priority = priority
    msg.actions.append(of.ofp_action_output(port = port))
    con.send(msg)

def brainwash(sid): # clean up all entry of a switch
    con = core.openflow.getConnection(sid)
    if not con:
      return
    msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
    con.send(msg)

def update_status(sid, flag):
  global status
  if flag:
    if (sid==4):
      status = status | 2
    elif (sid==5):
      status = status | 1
  else:
    if (sid==4):
      status = status & 1
    elif (sid==5):
      status = status & 2

class myDiscovery(Discovery):
  _timeout_check_period = 0.5

  def _expire_links (self):
    """
    Remove apparently dead links
    """
    now = time.time()

    expired = [link for link,timestamp in self.adjacency.iteritems()
               if timestamp + self._link_timeout < now]
    if expired:
      for link in expired:
        log.info('link timeout: %s', link)

      self._delete_links(expired)

class topoDiscovery(EventMixin):

    def __init__(self):
      def startup():
        core.openflow.addListeners(self, priority = 100)
        core.openflow_discovery.addListeners(self)
      core.call_when_ready(startup, ('openflow','openflow_discovery'))
      print "init over"

    def _handle_LinkEvent(self, event, delayed=False):
      l = event.link
      sw1 = l.dpid1
      sw2 = l.dpid2
      if (sw1 > sw2):
        sw1, sw2 = sw2, sw1
      pt1 = l.port1
      pt2 = l.port2

      if (event.added):
        print "Link UP between l%d and s%d" % (sw1, sw2)
      elif (event.removed):
        print "Link DOWN between l%d and s%d" % (sw1, sw2)

      if (event.added):
        link_state[sw2][sw1] = 1
        if (sum(link_state[sw2]) == 3):
          update_status(sw2, True)
          print_status()
          brainwash(sw1)
          for sid in range(1, 4):
            teach(status, sid)
      elif (event.removed):
        link_state[sw2][sw1] = 0
        if (sum(link_state[sw2]) != 3):
          update_status(sw2, False)
          print_status()
          brainwash(sw1)
          for sid in range(1, 4):
            teach(status, sid)

    def _handle_PacketIn(self, event):

      packet = event.parsed

      if isinstance(packet.payload, arp):
        print "GET ARP request"
        e = _handle_ARP_request(packet)
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
        msg.in_port = event.port
        event.connection.send(msg)

    def _handle_ConnectionUp(self, event):
      print("DPID:", event.dpid)
      sid = event.dpid
      teach(status, sid)
      print ''

def launch (disable_flood = False):
  global all_ports
  if disable_flood:
    all_ports = of.OFPP_ALL
  generate_tables()
  generate_arp_table()
  core.registerNew(myDiscovery, link_timeout = 1)
  core.registerNew(topoDiscovery)
