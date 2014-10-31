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

from .. import *

if is_virtual_environment():
    from ..player import base
elif is_console():
    from ..console import base
elif is_creating_loader(): 
    from ..loader import base

class ProcessorCommon(base.Base):
    def __init__(self, parent):
        base.Base.__init__(self, parent)

        self._interactors = []

    def registerInteractor(self, interactor):
        self._interactors.append(interactor)

    def unregisterInteractor(self, interactor):
        try:
            self._interactors.remove(interactor)
        except:
            pass

if is_virtual_environment():
    class Processor(ProcessorCommon):

        def __init__(self, parent):
            ProcessorCommon.__init__(self, parent)

        def setAsObjectToSynchronize(self, name):
            self.blenderVR.addObjectToSynchronize(self, name)

        def start(self):
            return

        def run(self):
            for interactor in self._interactors:
                interactor.run()

        def user_position(self, info):
            for user in info['users']:
                user.setPosition(info['matrix'])
            for interactor in self._interactors:
                interactor.user_position(info)

        def keyboardAndMouse(self, info):
            for interactor in self._interactors:
                if interactor.keyboardAndMouse(info):
                    break

        # Interactions between rendering nodes
        def sendToSlaves(self, command, argument = ''):
            self.blenderVR._sendToSlaves(command, argument)

        def receivedFromMaster(self, command, argument):
            self.logger.debug('Unknown command received from master:', command)

        # Interactions with the console
        def sendToConsole(self, command, argument = ''):
            self.blenderVR._controller.sendToConsole(command, argument)

        def receivedFromConsole(self, command, argument):
            for interactor in self._interactors:
                if interactor.receivedFromConsole(command, argument):
                    return
            self.logger.debug('Unknown command received from console:', command)

elif is_creating_loader(): 
    class Processor(ProcessorCommon):

        def __init__(self, parent):
            ProcessorCommon.__init__(self, parent)

elif is_console():
    class Processor(ProcessorCommon):

        def __init__(self, parent):
            ProcessorCommon.__init__(self, parent)

            self._main_profile = parent.profile
            try:
                from . import profile
                self._profile = profile.Profile(os.path.join(blenderVR_profilePath, 'processor', self._getProfileName()))
            except:
                self._profile = None

        @property
        def profile(self):
            return self._profile

        @property
        def main_profile(self):
            return self._main_profile

        def _getProfileName(self):
            return None

        def quit(self):
            for interactor in self._interactors:
                interactor.quit()

        def start(self):
            for interactor in self._interactors:
                interactor.start()

        def stop(self):
            for interactor in self._interactors:
                interactor.stop()

        def show(self):
            pass

        def hide(self):
            pass

        # Interactions with the Virtual Environment
        def sendToVirtualEnvironment(self, command, argument = ''):
            """
            Run arbitrary command in the virtual environment
            """
            self.getConsole().sendToVirtualEnvironment(command, argument)

        def receivedFromVirtualEnvironment(self, command, argument):
            for interactor in self._interactors:
                if interactor.receivedFromVirtualEnvironment(command, argument):
                    return
            self.logger.debug('Unknown command received from virtual environment:', command)

        def useLoader(self):
            return False
