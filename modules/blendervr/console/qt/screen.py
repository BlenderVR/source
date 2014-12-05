# -*- coding: utf-8 -*-
# file: blendervr/console/qt/screen.py

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

from ...tools.gui.qt import QtGui, QtCore, Dialog
from ..gui.screen import GUI as common_GUI
import os


class GUI(common_GUI):

    def __init__(self):
        common_GUI.__init__(self)

        self._window = Dialog(self, self.profile,
            {'window geometry': self._profile_index + ['log', 'geometry'],
             'display toggle': self._profile_index + ['log', 'toggle']})

        from ...tools import gui, getModulePath
        self._screen_ui = gui.load(os.path.join(getModulePath(), 'designer',
                                                'screen.ui'), self._window)
        self._screen_ui.std_out.clicked.connect(self.cb_toggle_stdout_state)
        self._screen_ui.std_err.clicked.connect(self.cb_toggle_stderr_state)

        self._window.setWindowTitle(self.getName())

        from . import logger
        self._logger_window = logger.Logger(self, self._profile_index + ['log'],
                                            self._screen_ui.log_window,
                                            self._screen_ui.log_level_selector)

    def __del__(self):
        common_GUI.__del__(self)

    def quit(self):
        common_GUI.quit(self)
        self._logger_window.quit()
        del(self._logger_window)
        del(self._window)

    def start(self):
        common_GUI.start(self)
        self._screen_ui.std_out.setChecked(self.profile.getValue(
                                self._profile_index + ['log', 'stdout']))
        self._screen_ui.std_err.setChecked(self.profile.getValue(
                                self._profile_index + ['log', 'stderr']))
        self._window.start()

    def getMenu(self, index):
        return self._window.getMenu(self.getName(), 'Ctrl+' + str(index))

    def is_log_window_opened(self):
        return self._window.isVisible()

    def _write_to_window(self, message):
        if self.is_log_window_opened():
            self._logger_window.write(message)

    def cb_toggle_stdout_state(self):
        self._logger_window.set_stream_state('stdout',
                                    self._screen_ui.std_out.isChecked())

    def cb_toggle_stderr_state(self):
        self._logger_window.set_stream_state('stderr',
                                    self._screen_ui.std_err.isChecked())

    def close(self):
        self._window.close()
