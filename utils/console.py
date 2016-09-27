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

    sys.path.append("/".join((BlenderVR_root, 'modules')))

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
            print("Current Configuration:")
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

    #Start launch mode
    elif __main__.environments.launch:
        #on-the-fly mode
        if sys.platform.startswith("win"):
            print("\tWindows doesn't currently supports BlenderVR in terminal mode")
        else:
            if __main__.environments.launch == "start":
                import blendervr.terminal.terminal
                console = blendervr.terminal.terminal.Terminal(__main__.profile_file, __main__.environments.config,
                                                       __main__.environments.blender_file, __main__.environments.processor_file,
                                                       __main__.environments.screen, True)
                console.start()

                if __main__.environments.log is not None:
                    console.log_in_file(__main__.environments.log)

                console.main()
                console.quit()
                del(console)
            #xml mode
            elif __main__.environments.launch == "start-xml":
                import blendervr.terminal.terminal
                data = get_data(__main__.environments.launch_xml)
                console = blendervr.terminal.terminal.Terminal(__main__.profile_file, data['configuration'],data['blender'],
                                                       data['processor'], data['screen'], True)

                console.start()

                if __main__.environments.log is not None:
                    console.log_in_file(__main__.environments.log)

                console.main()
                console.quit()
                del(console)

    #Start console mode
    elif __main__.environments.console_mode:
        if sys.platform.startswith("win"):
            print("\tWindows doesn't currently supports BlenderVR in terminal mode")
        else:
            import blendervr.terminal.terminal
            console = blendervr.terminal.terminal.Terminal(__main__.profile_file)
            console.start()
            console.main()
            console.quit()
            del(console)

    else:
        #Start GUI mode
        import blendervr.console.console
        console = blendervr.console.console.Console(__main__.profile_file)
        console.start()
        console.main()
        console.quit()
        del(console)


if not __main__.environments.console_mode and not __main__.environments.launch:
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
else:
	BlenderVR_QT = None

def get_data(xml_file):
    try:
        import xml.etree.ElementTree
        tree = xml.etree.ElementTree.parse(xml_file)
        root = tree.getroot()

        config = root.find('configuration-file').attrib['file']
        blender = root.find('blender').attrib['file']
        processor = root.find('processor').attrib['file']
        screen = root.find('default-screen').attrib['screen']

        data = {'configuration' : config,
                'blender' : blender,
                'processor' : processor,
                'screen' : screen,}

        is_valid_data = True
        for item in data:
            if item is None:
                is_valid_data = False

        if is_valid_data:
            return data

        else:
            print("Missing arguments in xml File")
            print("Not Valid XML File")
            return None

    except Exception as e:
        print(e)
        print("Not Valid XML File")
        return None

if __name__ == "__main__":
    main()

