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

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

import blendervr.tools.logger
logger = blendervr.tools.logger.getLogger('loader creation')
logger.addLoginWindow(blendervr.tools.logger.Console(''), True)

try:
    from blendervr import loader
    creator = loader.Creator(logger)

    creator.process()

except:
    logger.error(logger.EXCEPTION)
