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
    
    
def launch (address = '127.0.0.1', port = 6633, max_retry_delay = 16,
    dpid = None, ports = '', extra = None, ctl_port = None,
    __INSTANCE__ = None):
  
  """
  Create an 'arp' request and send it to the controller.
  """
  def action(event):

    sid_11 = '11'
    sw = do_launch(SoftwareSwitch, address, port, max_retry_delay, dpid=sid_11,
                    ports=2, extra_args=extra)
    core.raiseEvent(SwitchLaunchedEvent(), sid_11)
    
    r = arp()
    r.opcode = arp.REQUEST
    port1 = sw.ports[1]
    port2 = sw.ports[2]
    r.hwdst = port2.hw_addr # e.g: '02:00:01:01:00:02'
    r.hwsrc = port1.hw_addr

    r.protodst = IPAddr("0.0.0.0")#IP_ANY
    # src is IP_ANY
    eth1 = ethernet(type=ethernet.ARP_TYPE, src=port1.hw_addr, dst=port2.hw_addr)
    eth1.payload = r
    
    #send eth1 with the source as port1
    source = reactivex.of(sw).pipe(
        operators.delay(1.0)
     )
    source.subscribe(
        on_next = lambda i: sw.send_packet_in(in_port = port1.port_no, packet=eth1)#sendMessage(sid, msg)
     )
    
    #send another packet with the source as port2
    eth2 = ethernet(type=ethernet.ARP_TYPE, src=port2.hw_addr, dst=port1.hw_addr)
    eth2.payload = r
    source = reactivex.of(sw).pipe(
        operators.delay(3.0)
      )
    source.subscribe(
        on_next = lambda i: sw.send_packet_in(in_port = port2.port_no, packet=eth2)
      )
     

    #send eth1 again
    source = reactivex.of(sw).pipe(
        operators.delay(5.0)
      )
    source.subscribe(
        on_next = lambda i: sw.send_packet_in(in_port = port1.port_no, packet=eth1)
      )
    
    def sendMessage(sid, msg):
      dpid = int('0x'+sid, 16)
      connection = core.openflow.getConnection(dpid)
      connection.send(msg)
      
  core.addListenerByName("UpEvent", action)

