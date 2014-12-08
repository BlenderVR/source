#!/usr/bin/env python3

import sys
import os

def main():
    blenderVR_root    = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    blenderVR_modules = os.path.join(blenderVR_root, 'modules')
    sys.path.append(blenderVR_modules)

    from blendervr.tools import connector
    client = connector.Client('localhost:' + sys.argv[1], 'ui')
    #client.setCallback(self._waitForConfiguration)
    #client.setWait(True)
    
if __name__ == "__main__":
    main()
