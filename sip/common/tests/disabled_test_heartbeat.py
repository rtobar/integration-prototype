# coding: utf-8
""" Test of the heartbeat interface.

The heartbeat interface is used for health checking between the
Master Controller and Slaves.

Run with:
    $ python3 -m unittest -f -v sip.common.tests.test_heartbeat
or
    $ python3 -m unittest discover -f -v -p test_heartbeat.py
"""
import logging.handlers
import os
import sys
import time
import unittest
import warnings

import docker

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sip.common.docker_paas import DockerPaas as Paas


# @unittest.skip('Needs fixing.')
class HeartbeatTest(unittest.TestCase):
    """ Test of the Heartbeat interface.

    Makes use of the Docker PaaS interface to run a service and
    then checks for heartbeats.
    """
    @classmethod
    def setUpClass(cls):
        """ Initialise the test class.
        """
        warnings.simplefilter('ignore', ResourceWarning)

        # Get a client to the local docker engine.
        client = docker.from_env()

        # Skip the tests in this class if not running from a manager node.
        if not client.info()['Swarm']['ControlAvailable']:
            raise unittest.SkipTest('This test must be run from a swarm '
                                    'manager node.')
            # client.swarm.init()

        # Create a logging server
        # FIXME(BM): This should not be needed to test heartbeat!
        paas = Paas()
        cls.logger = paas.run_service(
            'logging_server',
            'sip',
            [logging.handlers.DEFAULT_TCP_LOGGING_PORT],
            ['python3', 'sip/common/logging_server.py'])

        # Wait for the logging server to come online.
        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        """ Tear down the test class.
        """
        cls.logger.delete()

    def setUp(self):
        """ Initialise the test case
        """
        warnings.simplefilter('ignore', ResourceWarning)
        paas = Paas()
        name = 'heartbeat_sender'
        task = 'sip'
        port = 12345
        cmd = ['python3', 'sip/common/tests/mock_heartbeat_sender.py']
        self.sender = paas.run_service(name, task, [port], cmd)
        self.sender_port = port
        time.sleep(3)

    def tearDown(self):
        """ Tear down the test case
        """
        self.sender.delete()

    def test_simple(self):
        """ Test for successful receive of heartbeat messages
        """
        # Import the heartbeat Listener class
        # (imports logging_api which needs the logging server to be running)
        from sip.common.heartbeat import Listener

        # Start the heartbeat listener and connect to the sender
        listener = Listener(timeout=2000)
        location = self.sender.location(self.sender_port)
        listener.connect(location[0], location[1])
        time.sleep(5)

        # for _ in range(20):
        #     msg = listener.listen()
        #     print('msg = ', msg)

        # Check that we have received heartbeat messages.
        received_count = 0
        fail_count = 0
        while received_count < 2:
            msg = listener.listen()
            # print("msg = '{}'".format(msg))
            if msg:
                received_count += 1
                self.assertEqual(msg[0], 'test')
                self.assertEqual(msg[1], 'ok')
            else:
                fail_count += 1
                if fail_count > 10:
                    self.fail('Failed to receive heartbeat messages.')
            time.sleep(0.5)
