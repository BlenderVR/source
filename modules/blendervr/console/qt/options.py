# -*- coding: utf-8 -*-
# file: blendervr/console/qt/options.py

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
from .. import base
from ..gui.options import GUI as common_GUI
import os


class GUI(base.Base, common_GUI):

    def __init__(self, parent):
        base.Base.__init__(self, parent)
        common_GUI.__init__(self)

        self._window = Dialog(self, self.profile,
                            {'window geometry': ['options', 'geometry'],
                             'display toggle': ['options', 'toggle']})

        from ...tools import gui, getModulePath
        self._options_ui = gui.load(os.path.join(getModulePath(),
                                    'designer', 'options.ui'), self._window)

        self._window.setWindowTitle('blenderVR options')

        self._options_ui.debug_daemon.stateChanged.connect(
                                                    self.cb_debug_daemon)
        self._options_ui.restart_daemons.clicked.connect(
                                                    self.cb_restart_daemons)
        self._options_ui.debug_processor.stateChanged.connect(
                                                    self.cb_debug_processor)
        self._options_ui.reload_processor.clicked.connect(
                                                    self.cb_reload_processor)
        self._options_ui.executables.stateChanged.connect(self.cb_executables)

    def __del__(self):
        common_GUI.__del__(self)

    def getMenu(self):
        return self._window.getMenu('Options', 'Ctrl+O')

    def quit(self):
        common_GUI.quit(self)
        del(self._window)

    def start(self):
        common_GUI.start(self)
        self._window.start()
        self._options_ui.debug_daemon.setChecked(
                            self.profile.getValue(['debug', 'daemon']))
        self._options_ui.debug_processor.setChecked(
                            self.profile.getValue(['debug', 'processor']))
        self._options_ui.executables.setChecked(
                            self.profile.getValue(['debug', 'executables']))

    def getmenu(self, index):
        return self._window.getMenu(self.getName(), 'Ctrl+O')

    def close(self):
        self._window.close()

    def cb_debug_daemon(self):
        self.profile.setValue(['debug', 'daemon'],
                                self._options_ui.debug_daemon.isChecked())

    def cb_executables(self):
        self.profile.setValue(['debug', 'executables'],
                               self._options_ui.executables.isChecked())

    def cb_debug_processor(self):
        self.profile.setValue(['debug', 'processor'],
                                self._options_ui.debug_processor.isChecked())

    def cb_restart_daemons(self):
        for name, obj in self.getConsole()._screens._screens.items():
            obj.restartDaemon()

    def cb_reload_processor(self):
        self.getConsole().update_user_files()

    def blenderVR_state_changed(self, state):
        self._options_ui.restart_daemons.setEnabled(state)
        self._options_ui.reload_processor.setEnabled(state)

