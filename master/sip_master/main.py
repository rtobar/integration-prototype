""" Master controller main program

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.
"""
__author__ = 'David Terrett + Brian McIlwrath'

import json
import threading
import subprocess
import signal
import os
import time

from sip_common.state_machine import StateMachine
from sip_common.resource_manager import ResourceManager
from sip_master.states import state_table
from sip_master.states import Standby
from sip_master.heartbeat_listener import HeartbeatListener
from sip_master import config
from sip_master.rpc_service import RpcService

def main(config_file, resources_file):

    # Create the resource manager
    with open(resources_file) as f:
        config.resource = ResourceManager(json.load(f))

    # "Allocate" a host for the master controller so that we can allocate it
    # resources.
    config.resource.allocate_host("Master Controller", {'host': 'localhost'}, 
            {})

    # Start logging server as a subprocess
    logserver = subprocess.Popen('common/sip_common/logging_server.py', 
            shell=True)
    # Wait until it initializes
    time.sleep(2)

    # Create the slave config array from the configuration (a JSON string)
    with open(config_file) as f:
        config.slave_config = json.load(f)

    # Create the master controller state machine
    config.state_machine = StateMachine(state_table, Standby)

    # Create and start the global heartbeat listener
    config.heartbeat_listener = HeartbeatListener(config.state_machine)
    config.heartbeat_listener.start()

    """ This starts the rpyc 'ThreadedServer' - this creates a new 
        thread for each connection on the given port
    """
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(RpcService,port=12345)
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    """ For testing we can also run events typed on the terminal
    """
    # Read and process events
    while True:
        event = input('?').split()
        if event:
            result = config.state_machine.post_event(event)

            if result == 'rejected':
                print('not allowed in current state')
            if result == 'ignored':
                print('command ignored')
            else:
                print('master controller state:', 
                        config.state_machine.current_state())
                if config.state_machine.current_state() == '_End':
                       print('Terminating logserver, pid ', logserver.pid)
                       os.kill(logserver.pid, signal.SIGTERM)