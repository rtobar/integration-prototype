# -*- coding: utf-8 -*-
#
# This file is part of the SDPMasterController project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

First go at a realistic SDP Master Controller
"""

__all__ = ["SDPMasterController", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property
from PyTango import AttrQuality,DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKAElementMaster import SKAElementMaster
# Additional import
# PROTECTED REGION ID(SDPMasterController.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SDPMasterController.additionnal_import


class SDPMasterController(SKAElementMaster):
    """
    First go at a realistic SDP Master Controller
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SDPMasterController.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SDPMasterController.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    operatingState = attribute(
        dtype='DevEnum',
        enum_labels=["STARTUP", "STANDY", "MAINT", "OPERATE", ],
    )
    processList = attribute(
        dtype='str',
        doc="JSON string list of Process Devices that exist. For each Process Device: device name, Scheduling Block ID, type of process (PSS, PST, Continuum Imaging, etc.)",
    )
    # -----
    # Pipes
    # -----

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAElementMaster.init_device(self)
        # PROTECTED REGION ID(SDPMasterController.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SDPMasterController.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SDPMasterController.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SDPMasterController.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_operatingState(self):
        # PROTECTED REGION ID(SDPMasterController.operatingState_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SDPMasterController.operatingState_read

    def read_processList(self):
        # PROTECTED REGION ID(SDPMasterController.processList_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SDPMasterController.processList_read

    # -------------
    # Pipes methods
    # -------------

    # --------
    # Commands
    # --------

    @command
    @DebugIt()
    def init(self):
        # PROTECTED REGION ID(SDPMasterController.init) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.init

    @command
    @DebugIt()
    def Standby(self):
        # PROTECTED REGION ID(SDPMasterController.Standby) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.Standby

    @command
    @DebugIt()
    def Disable(self):
        # PROTECTED REGION ID(SDPMasterController.Disable) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.Disable

    @command
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(SDPMasterController.On) ENABLED START #
        pass
        self.debug_stream("in ON command");
        # PROTECTED REGION END #    //  SDPMasterController.On

    @command(dtype_in='str', 
    doc_in="Takes JSON string as input parameter:\nprocessing type,\nnumber of baselines / beams,\nfrequency band extent,\nTBD", 
    dtype_out='int16', 
    doc_out="Returns ingest buffer availability for the processing specified \nin the input parameter as available ingest time, unit seconds."
    )
    @DebugIt()
    def getCapacity(self, argin):
        # PROTECTED REGION ID(SDPMasterController.getCapacity) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SDPMasterController.getCapacity

    @command(dtype_in='int16', 
    doc_in="Takes Scheduling Block ID as input parameter.", 
    )
    @DebugIt()
    def new(self, argin):
        # PROTECTED REGION ID(SDPMasterController.new) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.new

    @command(dtype_in='int16', 
    doc_in="Takes Scheduling Block ID as input parameter", 
    )
    @DebugIt()
    def delete(self, argin):
        # PROTECTED REGION ID(SDPMasterController.delete) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPMasterController.delete

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SDPMasterController.main) ENABLED START #
    from PyTango.server import run
    return run((SDPMasterController,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SDPMasterController.main

if __name__ == '__main__':
    main()
