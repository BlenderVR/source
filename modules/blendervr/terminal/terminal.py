
# -*- coding: utf-8 -*-
# file: blendervr/console/console.py

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

import sys
import os
import logging
import time

from .ui import argument as argument_handler
from .ui import ui
from ..console.logic import console as logic

try:
    import readline
except:
    pass


class Terminal(logic.Logic, ui.UI):
        def __init__(self, profile_file, config_file = None, blender_file = None, processor_file = None, screen = None, start = False):

            self.state = ""
            self.start_mode = start
            if start:
                self.launch_data = [config_file, blender_file, processor_file, screen]

            #initialize variables
            self._is_terminal_mode = True
            self._blender_file = None
            self._loader_file = None
            self._processor_files = None
            self._processor = None
            self._update_loader_script = os.path.join(BlenderVR_root, 'utils',
                                                    'update_loader.py')

            #Get profile file
            from . import profile
            self._profile = profile.Profile(profile_file)
            self._profile.setValue(['root'],BlenderVR_root)

            #If it's in start mode, turn silent mode off
            if self.start_mode:
                self._silent_mode = True
            else:
                self._silent_mode = self.profile.getValue(['terminal', 'silent_mode'])


            if self._silent_mode is None:
                self._silent_mode = self.profile.setValue(['terminal', 'silent_mode'], False)
                self._silent_mode = False

            #get the terminal log level
            try:
                self.log_level = self.profile.getValue(['terminal', 'log_level'])
            except:
                self.log_level = 'debug'

            if self.log_level is None:
                self.log_level = self.profile.setValue(['terminal', 'log_level'], 'debug')
                self.log_level = 'debug'

            #get Logger
            from ..tools import logger
            self._logger = logger.getLogger('BlenderVR')

            #if the application isn't in silent mode, initialize the output to the console
            if not self._silent_mode:
                self.initialize_console_logger()

            from ..plugins import getPlugins
            self._plugins = getPlugins(self, self._logger)

            from . import screens
            self._screens = screens.Screens(self)

            self.profile.setValue(['debug', 'daemon'], False)

            logic.Logic.__init__(self)
            ui.UI.__init__(self)


        #start
        def start(self):
            for plugin in self._plugins:
                plugin.start()
            self.profile.lock(False)
            logic.Logic.start(self)

        #main
        def main(self):
            ui.UI.main(self)

        #stop everything and quit application
        def quit(self):
            self.logger.debug("Quitting...")
            self.profile.lock(True)
            self.logger.debug("Closing plugins")
            for plugin in self._plugins:
                plugin.quit()
            logic.Logic.quit(self)
            del(self._screens)
            ui.UI.stop(self)
            self.logger.debug("Exiting application... ")
            sys.exit()

        def __del__(self):
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

        @property
        def is_terminal_mode(self):
            return self._is_terminal_mode

















