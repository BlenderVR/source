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
from .logic import console as logic
from .qt import console as gui


class ConsoleConsole(logic.Logic, gui.GUI):
    def __init__(self, profile_file):

        self._blender_file = None
        self._loader_file = None
        self._processor_files = None

        self._processor = None

        self._update_loader_script = "/".join((BlenderVR_root, 'utils',
                                                    'update_loader.py'))

        from . import profile
        self._profile = profile.Profile(profile_file)

        from ..tools import logger
        self._logger = logger.getLogger('BlenderVR')

        logic.Logic.__init__(self)
        gui.GUI.__init__(self)

        from . import screens
        self._screens = screens.Screens(self)

        from ..plugins import getPlugins
        self._plugins = getPlugins(self, self._logger)

    def __del__(self):
        pass

    def start(self):
        logic.Logic.start(self)
        gui.GUI.start(self)
        self._screens.start()
        self.load_configuration_file()
        for plugin in self._plugins:
            plugin.start()
        self.profile.lock(False)

    def quit(self):
        self.profile.lock(True)
        for plugin in self._plugins:
            plugin.quit()
        logic.Logic.quit(self)
        gui.GUI.quit(self)
        self._screens.quit()
        del(self._screens)
        gui.quit()
        sys.exit()

    @property
    def profile(self):
        return self._profile

    @property
    def logger(self):
        return self._logger

    @property
    def plugins(self):
        return self._plugins

Console = ConsoleConsole
