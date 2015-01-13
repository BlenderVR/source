# -*- coding: utf-8 -*-
# file: blendervr/tools/gui/qt.py

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

if blenderVR_QT == 'PyQt4':
    from PyQt4 import QtGui, QtCore
else:
    from PySide import QtGui, QtCore


class Common:
    def __init__(self, owner, profile, profile_indices):
        self._owner = owner
        self.profile = profile
        self._profile_indices = profile_indices

    def start(self):
        self.setGeometry()

    def setGeometry(self):
        geometry = self.profile.getValue(
                                self._profile_indices['window geometry'])
        if geometry is not None:
            self.resize(geometry[0], geometry[1])
            self.move(geometry[2], geometry[3])

    def resizeEvent(self, event):
        value = self.profile.getValue(self._profile_indices['window geometry'])
        if value is None or len(value) != 4:
            value = [0, 0, 0, 0]
        value[0] = event.size().width()
        value[1] = event.size().height()
        self.profile.setValue(self._profile_indices['window geometry'], value)
        super(Common, self).resizeEvent(event)

    def moveEvent(self, event):
        value = self.profile.getValue(self._profile_indices['window geometry'])
        if value is None or len(value) != 4:
            value = [0, 0, 0, 0]
        if self.pos().isNull():
            value[2] = 0
            value[3] = 0
        else:
            value[2] = self.pos().x()
            value[3] = self.pos().y()
        self.profile.setValue(self._profile_indices['window geometry'], value)
        super(Common, self).moveEvent(event)


class Dialog(Common, QtGui.QDialog):
    def __init__(self, owner, profile, profile_indices):
        QtGui.QDialog.__init__(self)
        Common.__init__(self, owner, profile, profile_indices)
        QtGui.QDialog.setWindowFlags(self,
                    QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint)
        self.finished.connect(self.cb_close)

    def start(self):
        Common.start(self)
        self._display_log_window(self.profile.getValue(
                                self._profile_indices['display toggle']))

    def cb_close(self):
        self._display_log_window(False)

    def getMenu(self, name, shortcut):
        if not hasattr(self, '_consoleMenu'):
            self._consoleMenu = QtGui.QAction(
                                self._owner.getConsole().getWindow())
            self._consoleMenu.setCheckable(True)
            self._consoleMenu.setObjectName(name)
            self._consoleMenu.setText(name)
            self._consoleMenu.triggered.connect(self.cb_display_log_window)
            self._consoleMenu.setShortcut(QtGui.QApplication.translate(
                    name, shortcut, None, QtGui.QApplication.UnicodeUTF8))
        return self._consoleMenu

    def setMenuAction(self, menu_action):
        self._consoleMenu = menu_action
        self._consoleMenu.triggered.connect(self.cb_display_log_window)

    def cb_display_log_window(self):
        self._display_log_window(self._consoleMenu.isChecked())

    def _display_log_window(self, display):
        self._consoleMenu.setChecked(display)
        if self.isVisible() != display:
            self.setVisible(display)
        self.profile.setValue(self._profile_indices['display toggle'], display)

