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
from . import Interactor
from ..tools.connector import Common

COMMON_NAME = 'land marks'

# From Virtual environment to Console
LANDMARKS = 'landmarks'
USERS     = 'users'
USER      = 'user'

# From Console to Virtual environment
SAVE   = 'save'
LOAD   = 'load'
REMOVE = 'remove'
USER   = 'user'

if is_virtual_environment():

    import bge
    import copy
    import mathutils

    class LandMarks(Interactor):
        def __init__(self, parent, name = COMMON_NAME):
            Interactor.__init__(self, parent)
            self._name = name

            if 'landmarks' not in bge.logic.globalDict['blenderVR']['interactors']:
                bge.logic.globalDict['blenderVR']['interactors']['landmarks'] = {}

            self._positions = bge.logic.globalDict['blenderVR']['interactors']['landmarks']

            self.sendToConsole(self._name, Common.composeMessage(USERS,list(self.blenderVR.getAllUsers().keys())))
            users = self.blenderVR.getScreenUsers()
            if self.blenderVR.isMaster() and (len(users) == 1):
                self._user = users[0]
                self.sendToConsole(self._name, Common.composeMessage(USER, self._user.getName()))
                self._send()

        def _send(self):
            self.sendToConsole(self._name, Common.composeMessage(LANDMARKS, list(self._positions.keys())))

        def receivedFromConsole(self, command, argument):
            if command != self._name:
                return False
            if not hasattr(self, '_user'):
                return True
            command, argument = Common.decomposeMessage(argument)
            if command == SAVE:
                transform = self._user.localTransform
                self._positions[argument] = ((transform[0][0], transform[0][1], transform[0][2], transform[0][3]),
                                             (transform[1][0], transform[1][1], transform[1][2], transform[1][3]),
                                             (transform[2][0], transform[2][1], transform[2][2], transform[2][3]),
                                             (transform[3][0], transform[3][1], transform[3][2], transform[3][3]))
                bge.logic.saveGlobalDict()
                self._send()
            if command == LOAD:
                if argument in self._positions:
                    self._user.setVehiclePosition(mathutils.Matrix(self._positions[argument]))
            if command == REMOVE:
                if argument in self._positions:
                    del(self._positions[argument])
                    self._send()
            if command == USER:
                try:
                    self._user = self.blenderVR.getUserByName(argument)
                except:
                    pass
            return True

else:

    import os
    from ..tools.gui.qt import QtGui

    class LandMarks(Interactor):
        def __init__(self, parent, name = COMMON_NAME):
            Interactor.__init__(self, parent)
            self._name = name

            self._widget = QtGui.QWidget()
            from ..tools import gui, getModulePath
            self._ui = gui.load(os.path.join(getModulePath(), 'designer', 'landmark.ui'), self._widget)
            self._ui.save.clicked.connect(self.cb_save)
            self._ui.select.clicked.connect(self.cb_select)
            self._ui.remove.clicked.connect(self.cb_remove)
            self._ui.users.currentIndexChanged.connect(self.cb_select_user)

        def registerWidget(self, parent_widget):
            from ..tools.gui import insertWidgetInsideAnother
            insertWidgetInsideAnother(parent_widget, self._widget)

        def receivedFromVirtualEnvironment(self, command, argument):
            if self._name != command:
                return False
            command, argument = Common.decomposeMessage(argument)
            if command == LANDMARKS:
                self._ui.available.reset()
                argument.sort()
                for landmark in argument:
                    self._ui.available.addItem(landmark)
            if command == USERS:
                self._ui.users.clear()
                argument.sort()
                for user in argument:
                    self._ui.users.addItem(user)
            if command == USER:
                index = self._ui.users.findText(argument)
                if index >= 0:
                    self._ui.users.setCurrentIndex(index)
            return True

        def cb_save(self):
            name = self._ui.name.text()
            if name:
                self.sendToVirtualEnvironment(self._name, Common.composeMessage(SAVE, name))

        def cb_select(self):
            if self._ui.available.currentItem():
                self.sendToVirtualEnvironment(self._name, Common.composeMessage(LOAD, self._ui.available.currentItem().text()))

        def cb_remove(self):
            if self._ui.available.currentItem():
                self.sendToVirtualEnvironment(self._name, Common.composeMessage(REMOVE, self._ui.available.currentItem().text()))

        def cb_select_user(self):
            if self._ui.users.currentText():
                self.sendToVirtualEnvironment(self._name, Common.composeMessage(USER, self._ui.users.currentText()))
