
import os
print os.path.dirname(__file__)

import sys

if sys.platform == "win32":
	from windows import *
else:
	raise Exception("The %s platform is not supported. Aborting." % sys.platform)
