# -*- coding: utf-8 -*-
# file: blendervr/console/screen.py

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

from . import base
from ..console.logic import screen as logic



class Screen(base.Base, logic.Logic):

    def __init__(self, screens, name, net_console):
        self._opened = True
        base.Base.__init__(self, screens)
        self._main_logger = self.getParent().logger
        self._name = name

        self._blender_file = None
        self._loader_file = None
        self._processor_files = []

        from ..tools import logger
        self._logger = logger.getLogger(self.getName())

        logic.Logic.__init__(self, net_console)
        self.main_logger.debug('Creation of screen "' + self.getName() + '"')

    def __del__(self):
        self.main_logger.debug('Deletion of screen "' + self.getName() + '"')
        logic.Logic.__del__(self)

    def start(self):
        logic.Logic.start(self)

    def quit(self):
        logic.Logic.quit(self)

    def getName(self):
        return self._name

    def _write_to_window(self, message):
        if message[:7] == 'stderr>':
            print(message[7:])
        elif message[:7] == 'stdout>':
            print(message[7:])
        elif message.startswith("INFO>"):
            self.logger.info(message[5:])
        elif message.startswith('DEBUG>'):
            self.logger.debug(message[6:])

    @property
    def logger(self):
        return self._main_logger

    @property
    def main_logger(self):
        return self._main_logger

    def is_log_window_opened(self):
        return self._opened
