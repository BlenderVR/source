
import os

import sys

if "win" in sys.platform:
	from windows import *
else if "linux" in sys.platform:
    from linux import *
else:
	raise Exception("The %s platform is not supported. Aborting." % sys.platform)
