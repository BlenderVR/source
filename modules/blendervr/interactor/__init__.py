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

from .. import is_virtual_environment

if is_virtual_environment():

    import bge

    if 'interactors' not in bge.logic.globalDict['blenderVR']:
        bge.logic.globalDict['blenderVR']['interactors'] = {}


    from ..player import base

    class Interactor(base.Base):
        def __init__(self, parent):
            base.Base.__init__(self, parent)

        def user_position(self, info):
            pass

        def keyboardAndMouse(self, info):
            return False

        def run(self):
            pass

        # # Interactions between rendering nodes
        # def sendToSlaves(self, command, argument = ''):
        #     self.blenderVR._sendToSlaves(command, argument)

        # def receivedFromMaster(self, command, argument):
        #     return False

        # Interactions with the console
        def sendToConsole(self, command, argument = ''):
            self.blenderVR._controller.sendToConsole(command, argument)

        def receivedFromConsole(self, command, argument):
            return False

else:

    from ..console import base

    class Interactor(base.Base):
        def __init__(self, parent):
            base.Base.__init__(self, parent)

        def quit(self):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        # Interactions with the virtual environment
        def sendToVirtualEnvironment(self, command, argument = ''):
            self.getConsole().sendToVirtualEnvironment(command, argument)

        def receivedFromVirtualEnvironment(self, command, argument):
            return False
