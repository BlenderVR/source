# -*- coding: utf-8 -*-
# file: utils/update_loader.py

"""
Update Loader
*************

Script that runs in Blender in background mode to transform the ``.blend``
file into a Blender-VR ready file.
A few Logic Bricks are created among other changes in the initial scene.
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

import blendervr.tools.logger
logger = blendervr.tools.logger.getLogger('loader creation')

class Logger_Handler(blendervr.tools.logger.Handler):
    def __init__(self, logger, context):
        blendervr.tools.logger.Handler.__init__(self, logger)
        self._context = context

    def emit(self, record):
        print(json.dumps({'logger': self._getLogFromRecord(record, self._context)}))

Logger_Handler(logger, 'updater')

try:
    from blendervr import loader
    creator = loader.Creator(logger)

    creator.process()

except:
    logger.error(logger.EXCEPTION)
