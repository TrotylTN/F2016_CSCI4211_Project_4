from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.revent import * 

"""
Forwarding tables
forwarding[STATUS][SWITCH][(SRC_MAC, DST_MAC)] = (PORT, PRIORITY)
means that when the SWITCH receive a packet matches (SRC_MAC, DST_MAC) under STATUS, it should
forward it to PORT and this row have PRIORITY. Both SRC_MAC and DST_MAC can be -1 (not together)
which means this role does not match SRC_MAC/DST_MAC.
E.g. forwarding[3][1][(H1_MAC, -1)] = (1, 100)
"""
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

def role_generator(status, sid):
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

def generate_role_tables():
  for s in range(1, 4):
    for switch in range(1, 6):
      role_generator(s, switch)  

"""
Show the status of two spine switch
True means it is on, False means it is off.
"""
def print_status():
  global status
  state = [status // 2 != 0, status % 2 != 0]
  for i in range(2):
    if state[i]:
      state[i] = "S%d: ON" % (i+4)
    else:
      state[i] = "S%d: OFF" % (i+4)
  print "Status: ", state

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

def _handle_PacketIn(event):
  packet = event.parsed
  if isinstance(packet.payload, arp):
    print "GET ARP request"
    e = _handle_ARP_request(packet)
    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
    msg.in_port = event.port
    event.connection.send(msg)

def _handle_ConnectionUp(event):
  sid = event.dpid
  teach(status, sid)

def _handle_PortStatus (event):
  """
  Link down/up will trigger this handler with both sides of a link
  and we only run this handler when the switch is a spine switch.
  """
  if event.dpid not in [4, 5]:
    return
  """
  Every link down/up with trigger this handler twice and the first 
  time the state=0 and config=1. The second time for link down is 
  state=1 and config=1 and for link up is state=0 and config=0. We
  only handle the second call and use this feature to distinguish
  between link down and link up.
  """
  if (event.ofp.desc.state != event.ofp.desc.config):
    return
  if (not event.modified):
    return
  else:
    if (event.ofp.desc.state == 0):
      flag = True
    elif (event.ofp.desc.state == 1):
      flag = False
    else:
      return
  port = int(event.port)
  swid = int(event.dpid)
  if (flag):
    print "Link up"
    link_state[swid][port] = 1
    # Turn a switch on iff all of its three links is up.
    if (sum(link_state[swid]) == 3):
      update_status(swid, True)
      print_status()
      for sid in range(1, 4):
        brainwash(sid)
        teach(status, sid)
  else:
    print "Link down"
    # Turn a switch off once one of its three links is down.
    link_state[swid][port] = 0
    if (sum(link_state[swid]) != 3):
      update_status(swid, False)
      print_status()
      for sid in range(1, 4):
        brainwash(sid)
        teach(status, sid)

def launch (disable_flood = False):
  global all_ports
  if disable_flood:
    all_ports = of.OFPP_ALL
  generate_role_tables()
  generate_arp_table()
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  core.openflow.addListenerByName("PortStatus", _handle_PortStatus)