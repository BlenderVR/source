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

from ..tools import getRootPath
import socket
import select
from .. import base
import os

class Daemon():
    def __init__(self, profile_file, debug):

        self._debug = debug
        
        # Simulation informations
        self._blender_file       = None 
        self._loader_file        = None
        self._processor_files    = None

        self._possibleScreenSets = None
        self._currentScreenSet   = None
        self._anchor             = None
        self._previous_state     = None
        self._common_processors  = []

        self._uis                = {}
        
        self._processor          = None

        self._update_loader_script = os.path.join(getRootPath(), 'utils', 'update_loader.py')

        from . import profile
        self._profile = profile.Profile(profile_file)

        from ..tools import logger
        self._logger = logger.getLogger('blenderVR')

        if self._debug:
            # Define connexions until the controller is running ...
            console_logger = logger.Console()
            self._default_logger = self._logger.addLoginWindow(console_logger, True)
            self._logger.setLevel('debug')

        from . import screens
        self._screens = screens.Screens(self)

        from ..plugins import getPlugins
        self._plugins = getPlugins(self, self._logger)

    def start(self):
        from ..tools import connector
        self._listener = connector.Listener(self._process_client)

        print('port:', self._listener.getPort())
        from .. import version
        self.logger.info('blenderVR version:', version)

    def main(self):
        self._listener.select()

    def _process_client(self, module, complement = ''):
        if module == 'ui':
            from . import ui
            new_ui = ui.UI(self, client, complement)
            self.main.addCallback(
            
        # if module == 'daemon' or module == 'blender_player':
        #     screen = self._screens.getScreen(complement)
        #     if screen:
        #         screen.setNetworkClient(module, client, addr)
        
    def quit(self):
        pass

    @property
    def profile(self):
        return self._profile

    @property
    def logger(self):
        return self._logger

    @property
    def plugins(self):
        return self._plugins
