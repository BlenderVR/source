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

import os
import sys
from . import ui
from . import daemon

class Controller():
    def __init__(self, profile_file, debug):

        self._debug = debug
        
        # Simulation informations
        self._blender_file       = None 
        self._loader_file        = None
        self._processor_files    = None

        self._anchor             = None
        self._previous_state     = None
        self._common_processors  = []

        self._uis                = []
        
        self._processor          = None

        self._controller_address = None

        from ...tools import getRootPath
        self._update_loader_script = os.path.join(getRootPath(), 'utils', 'update_loader.py')

        from . import profile
        self._profile = profile.Profile(profile_file)

        from ...tools import logger
        self._logger = logger.getLogger('blenderVR')
        
        if self._debug:
            # Define connexions until the controller is running ...
            console_logger = logger.Console()
            self._default_logger = self._logger.addLoginWindow(console_logger, True)
            self._logger.setLevel('debug')
            self.profile.setValue(['debug', 'daemon'], True)
            self.profile.setValue(['debug', 'executables'], True)

        from . import screens
        self._screens = screens.Screens(self)

        from ...plugins import getPlugins
        self._plugins = getPlugins(self, self._logger)

        from . import configuration
        self._configuration = configuration.Configuration(self)

    def start(self):
        from . import listener
        self._listener = listener.Listener(self)

        sys.stdout.write(str(self.getPort()) + "\n")
        sys.stdout.flush()
        from ... import version
        self.logger.info('blenderVR version:', version)
        self.configuration()
        
    def getPort(self):
        return self._listener.getPort()

    def getControllerAddress(self):
        return self._controller_address
    
    def main(self):
        while True:
            try:
                self._listener.select()
            except (KeyboardInterrupt, SystemExit):
                break

    def quit(self):
        pass

    def _create_client(self, client):
        type = client.getType()
        if type == 'UI':
            userInterface = ui.UI(self, client)
            self._uis.append(userInterface)
            return userInterface
        if type == 'daemon':
            daemonClient = daemon.Daemon(self, client)
            self._screens.appendClient(daemonClient)
            return daemonClient
        # if module == 'daemon' or module == 'blender_player':
        #     screen = self._screens.getScreen(complement)
        #     if screen:
        #         screen.setNetworkClient(module, client, addr)
        self.logger.error('Cannot understand client type :', type)

    def _delete_client(self, client):
        if client in self._uis:
            self._uis.remove(client)
            return
        # if module == 'daemon' or module == 'blender_player':
        #     screen = self._screens.getScreen(complement)
        #     if screen:
        #         screen.setNetworkClient(module, client, addr)

    def configuration(self):
        """
        Called whenever the configuration file changed (file modified or user choose another file) 
        """
        self._configuration.load()

    def screenSets(self, screenSets):
        """
        Called by the configuration file loader
        """
        self._screenSets = screenSets
        self.screenSet()

    def getScreenSets(self):
        return self._screenSets
            
    def screenSet(self):
        self.updateConfiguration()

    def updateConfiguration(self):
        configuration = self._configuration.getConfiguration()

        self._controller_address = configuration['console']['controller'] + ':' + str(self.getPort())
        self._screens.setConfiguration(configuration['screens'])
        del(configuration['screens'])
        #import pprint
        #pprint.pprint(configuration)



        self.runAction('start', 'daemon')

    def getCommonConfiguration(self):
        return None

    @property
    def profile(self):
        return self._profile

    @property
    def logger(self):
        return self._logger

    @property
    def plugins(self):
        return self._plugins

    def runAction(self, action, element):
        self._screens.runAction(action, element)
