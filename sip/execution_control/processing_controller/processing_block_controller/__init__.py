# coding=utf-8
"""Processing Block Controller module."""
__subsystem__ = 'ExecutionControl'
__service_name__ = 'ProcessingBlockController'
__version_info__ = (1, 1, 2)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
import logging
LOG = logging.getLogger('sip.ec.processing_block_controller')
