# -*- coding: utf-8 -*-
# file: utils/console.py

## Copyright (C) LIMSI-CNRS (2014)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer,
##
## This software is a computer program whose purpose is to distribute
## blender to render on Virtual Reality device systems.
##
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use,
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info".
##
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability.
##
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or
## data to be ensured and,  more generally, to use and operate it in the
## same conditions as regards security.
##
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
##

"""
BlenderVR Console
******************

BlenderVR console mode
"""

import sys
import os
import __main__


def main():
    import builtins
    builtins.BlenderVR_QT = BlenderVR_QT

    sys.path.append(os.path.join(BlenderVR_root, 'modules'))

    if __main__.environments.d_version:
        try:
            import blendervr
            print('Current version:', blendervr.version)
        except:
            pass
        sys.exit()

    if __main__.environments.dis_console:
        try:
            import pickle
            with open(__main__.profile_file, 'rb') as node:
                consoleuration = pickle.load(node)
            import pprint
            print("Consoleuration:")
            pprint.pprint(consoleuration)
        except:
            print('Invalid profile file:', __main__.profile_file)
        sys.exit()

    if __main__.environments.del_console:
        try:
            os.remove(__main__.profile_file)
        except:
            pass
        sys.exit()

    import blendervr.console.console
    console = blendervr.console.console.Console(__main__.profile_file)
    console.start()
    console.main()
    console.quit()
    del(console)


try:
    import PyQt4
    BlenderVR_QT = 'PyQt4'
except:
    try:
        import PySide
        BlenderVR_QT = 'PySide'
    except:
        print('No graphic library available : quitting !')
        sys.exit()


if __name__ == "__main__":
    main()

