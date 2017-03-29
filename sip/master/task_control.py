# -*- coding: utf-8 -*-
""" Functions for commanding a slave controller to load and unload tasks

FIXME(FD) Rename this file to slave_task_controller.py ?
"""

import os
import re

import rpyc

from sip.common.logging_api import log
from sip.common.resource_manager import ResourceManager
from sip.master import config


class SlaveTaskController:
    """Base class to define the slave task controller interface.

    This commands the slave controller to start and stop tasks.
    """
    def __init__(self):
        pass

    def shutdown(self):
        """Command the slave controller to shut down."""
        raise RuntimeError("Implement TaskController.shutdown().")

    def start(self, name, cfg, status):
        """Command the slave controller to load a task.

        Args:
            name (str): Name of the capability (slave/task name).
            cfg (dict): Configuration for the capability (from slave_map.json).
            status (dict): Slave status dictionary.
        """
        raise RuntimeError("Implement TaskController.start().")

    def stop(self):
        """Command the slave controller to unload the task."""
        raise RuntimeError("Implement TaskController.stop().")


class SlaveTaskControllerRPyC(SlaveTaskController):
    """Implementation of a slave task controller using RPyC."""
    def __init__(self):
        SlaveTaskController.__init__(self)
        self._conn = None

    def connect(self, address, port):
        """Establishes an RPyC connection."""
        log.debug('Connecting to {}:{}'.format(address, port))
        self._conn = rpyc.connect(address, port)

    def shutdown(self):
        """Command the slave controller to shut down."""
        log.debug('shutting down task')
        if self._conn is None:
            log.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.shutdown()

    def start(self, name, cfg, status):
        """Command the slave controller to load a task.

        Args:
            name (str): Name of the capability (slave/task name).
            cfg (dict): Configuration for the capability (from slave_map.json).
            status (dict): Slave status dictionary.
        """
        # Scan the task parameter list for entries with values starting with
        # a # character, or contained in a hash followed by curly brackets
        # (ie. #{...}), and replace with an allocated resource.
        log.debug('[SlaveTaskControllerRPyC] Starting task {}'.format(name))
        task_cfg = cfg['task']
        for i, value_str in enumerate(task_cfg):
            task_cfg[i] = self._set_resource(value_str, name, config.resource)

        # Send the slave the command to load the task
        if self._conn is None:
            log.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.load(task_cfg, cfg['task_control_module'])

    def stop(self):
        """Command the slave controller to unload the task."""
        if self._conn is None:
            log.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.unload()

    @staticmethod
    def _set_resource(value_str, name, resource_manager: ResourceManager):
        """Set the values of resources in task configuration strings.

        This replaces values starting with '#' or '#' followed by
        curly brackets (ie. #{...}) with resources obtained from the
        ResourceManager.
        """
        def _replace(match):
            """Replacement function."""
            value = match.groups()[0]
            # FIXME(BM) calling allocate_resource() is not ideal ...
            # should be get_resource()? instead and this function can
            # allocate if needed?
            return str(resource_manager.allocate_resource(name, value))

        s = re.sub(r'^#(\w+)$', _replace, value_str)
        return re.sub(r'#{(\w+)}', _replace, s)