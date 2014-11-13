import sys
import os
import builtins

builtins.blenderVR_root = os.path.dirname(os.path.dirname(__file__))
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
