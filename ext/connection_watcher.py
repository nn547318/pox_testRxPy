# Copyright 2013 <Your Name Here>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pox.core import core
from pox.lib.util import dpid_to_str

log = core.getLogger()

class MyComponent (object):
  def __init__ (self):
    core.openflow.addListeners(self)
    log.info("Watching event up...")

  def _handle_ConnectionUp (self, event):
    log.info("Switch %s has come up.", dpid_to_str(event.dpid))
    
  def _handle_PortStatus (self, event):
    if event.added:
      action = "added"
    elif event.deleted:
      action = "removed"
    else:
      action = "modified"
    log.info("Port %s on Switch %s has been %s." % (event.port, event.dpid, action))

def launch ():
  core.registerNew(MyComponent)



