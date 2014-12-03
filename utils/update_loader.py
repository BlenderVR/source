"""
Update Loader
*************

Script that runs in Blender in background mode to transform the ``.blend`` file into a Blender-VR ready file.
A few Logic Bricks are created among other changes in the initial scene.
"""

import sys
import os
import builtins

blenderVR_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(blenderVR_root, 'modules'))

import blendervr.tools.logger
logger = blendervr.tools.logger.getLogger('loader creation')
logger.addLoginWindow(blendervr.tools.logger.Console(''), True)


try:
    from blendervr import loader
    creator = loader.Creator(logger)

    creator.process()

except:
    logger.log_traceback(True)
