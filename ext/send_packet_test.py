#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 10:55:34 2022

@author: nanjiang
"""

from pox.core import core
from pox.datapaths import do_launch
from pox.datapaths import SwitchLaunchedEvent

from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp

import pox.openflow.libopenflow_01 as of

# from pox.datapaths.pcap_switch import PCapSwitch
from pox.datapaths.switch import SoftwareSwitch
import reactivex
from reactivex import operators
from reactivex.scheduler import ThreadPoolScheduler
import random
import time
import multiprocessing

_switches = {}


class SendPacketTest (object):
  def __init__ (self):
    self.connection = None
    core.addListeners(self)
    core.openflow.addListeners(self)
    print('addListeners----------------')
    
  # def _handle_ConnectionUp(self, event):
  #   print('connection up----------------')
  #   self.connection = event.connection
  #   _switches[0].set_connection(self.connection)
    
def launch (address = '127.0.0.1', port = 6633, max_retry_delay = 16,
    dpid = None, ports = '', extra = None, ctl_port = None,
    __INSTANCE__ = None):

  # core.registerNew(MyComponent)
  # core.registerNew(SendPacketTest)
  # _ports = ports.strip()
  
  """
  """

        
  def action(event):

    sid = '12'
    sw = do_launch(SoftwareSwitch, address, port, max_retry_delay, dpid=sid,
                    ports=2, extra_args=extra)
                    #magic_virtual_port_names = True)
    _switches[0] = sw
    core.raiseEvent(SwitchLaunchedEvent(), sid)
    # print('switch ports:', sw.ports)
    
    r = arp()
    r.opcode = arp.REQUEST
    r.hwdst = EthAddr('02:00:01:01:00:02')
    r.hwsrc = EthAddr('02:00:01:01:00:01')
    r.protodst = IPAddr("127.0.0.1")
    # src is IP_ANY
    eth = ethernet(type=ethernet.ARP_TYPE, src=r.hwsrc, dst=r.hwdst)
    eth.payload = r
    # log.debug("%i %i sending ARP REQ to %s %s",
    #           macEntry.dpid, macEntry.port, str(r.hwdst), str(r.protodst))
    port_no = sw.ports[2].port_no #type of port: pox.openflow.libopenflow_01.ofp_phy_port
    
    source = reactivex.of(sw).pipe(
        operators.delay(3.0)
        )
    source.subscribe(
        on_next = lambda i: sw.send_packet_in(in_port = port_no, packet=eth)#sendMessage(sid, msg)
        )
    
    def sendMessage(sid, msg):
      dpid = int('0x'+sid, 16)
      connection = core.openflow.getConnection(dpid)
      connection.send(msg)
      
  core.addListenerByName("UpEvent", action)

