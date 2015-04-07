# -*- coding: utf-8 -*-
# file: blendervr/interactor/head_controlled_navigation.py

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
from . import Interactor
import os

COMMON_NAME = 'update HC Nav'

if is_virtual_environment():
    import mathutils
    import math
    from ..base import Base
    from ..player.user import User

    class _HCNav(Base):
        def __init__(self, parent, element, method):
            super(_HCNav, self).__init__(parent)

            self._element = element
            self._method = method
            self.reset()
            self._positionFactors = [{}, {}, {}]
            self._orientationFactors = {}
            self._headNeckLocation = mathutils.Matrix.Translation(
                                                        (0.0, -0.15, 0.12))

            # Default factors
            self.setPositionFactors(0, 0.5, 3)
            self.setPositionFactors(1, 0.5, 3)
            self.setPositionFactors(2, 0.5, 3)
            self.setOrientationFactors(0.07, 2)

        def reset(self):
            self._position = mathutils.Vector((0.0, 0.0, 0.0))
            self._quaternion = mathutils.Quaternion()
            self._orientation = mathutils.Matrix()
            self._orientation_inverted = mathutils.Matrix()
            self._calibrate = False
            self._run = False
            self._calibrated = False

        def setPositionFactors(self, component, attenuation, power, max=1.0):
                                                        # should be a vector
            self._positionFactors[component]['attenuation'] = attenuation
            self._positionFactors[component]['power'] = power
            self._positionFactors[component]['max'] = max

        def setOrientationFactors(self, attenuation, power, max=1.0):
                                                        # should be a vector
            self._orientationFactors['attenuation'] = attenuation
            self._orientationFactors['power'] = power
            self._orientationFactors['max'] = max

        def setHeadNeckLocation(self, location):
            self._headNeckLocation = location

        def calibration(self):
            self._calibrate = True

        def update(self, newState):
            if newState == HCNav.CALIBRATE:
                self._calibrate = True
            elif newState == HCNav.START:
                if self._calibrated:
                    self._run = True
                else:
                    self.logger.warning('cannot start while not calibrated !')
            elif newState == HCNav.STOP:
                self._run = False
            elif newState == HCNav.TOGGLE:
                if self._run:
                    self._run = False
                else:
                    if self._calibrated:
                        self._run = True
                    else:
                        self.logger.warning(
                                        'cannot start while not calibrated !')
            elif newState == HCNav.RESET:
                self.reset()

        def setHeadLocation(self, matrix, info):
            matrix = matrix * self._headNeckLocation
            if self._calibrate:
                self._position = matrix.to_translation()
                self._quaternion = matrix.to_quaternion()
                self._orientation = matrix.to_3x3()
                self._orientation_inverted = \
                                    self._orientation_inverted.inverted()
                self._calibrate = False
                self._calibrated = True

            if not self._run:
                return

            position = (self._position - matrix.to_translation())
            for i in range(0, 3):
                scalePosition = position[i]
                if (scalePosition < 0):
                    scalePosition *= -1
                scalePosition *= self._positionFactors[i]['attenuation']
                scalePosition = math.pow(scalePosition,
                                         self._positionFactors[i]['power'])
                if scalePosition > self._positionFactors[i]['max']:
                    scalePosition = self._positionFactors[i]['max']
                position[i] *= scalePosition

            quat_o = self._quaternion
            quat_d = matrix.to_quaternion()

            scaleOrientation = quat_o.slerp(quat_d, 1).angle
            scaleOrientation *= self._orientationFactors['attenuation']
            scaleOrientation = math.pow(scaleOrientation,
                                        self._orientationFactors['power'])
            if scaleOrientation > self._orientationFactors['max']:
                scaleOrientation = self._orientationFactors['max']
            orientation = quat_o.slerp(quat_d, scaleOrientation)

            orientation = orientation.to_matrix().inverted() * self._orientation

            delta = orientation.to_4x4() * \
                                    mathutils.Matrix.Translation(position)

            if self._method is not None:
                self._method(delta, info)
            elif isinstance(self._element, User):
                self._element.setVehiclePosition(
                                delta * self._element.getVehiclePosition())

        def getNavigationState(self):
            return self._run

    class HCNav(Interactor):
        CALIBRATE = 'calibrate'
        START = 'start'
        STOP = 'stop'
        TOGGLE = 'toggle'
        RESET = 'reset'

        def __init__(self, parent, method=None, one_per_user=True):
            super(HCNav, self).__init__(parent)

            self._default_user = None
            self._interactor_name = COMMON_NAME

            if one_per_user:
                for user_name, user in self.BlenderVR.getAllUsers().items():
                    user._HCNav = _HCNav(self, user, method)
            elif hasattr(method, '__call__'):
                self._local = _HCNav(self, None, method)
            else:
                from ..player import exceptions
                raise exceptions.Processor('Invalid method or processor !')

        def setDefaultUser(self, user):
            self._default_user = user

        def setPositionFactors(self, component, attenuation, power, max=1.0,
                                                                    user=None):
                                                        # should be a vector
            if hasattr(self, '_local'):
                self._local.setPositionFactors(component, attenuation,
                                                                power, max)
                return
            if user is None:
                for user_name, user in self.BlenderVR.getAllUsers().items():
                    user._HCNav.setPositionFactors(component, attenuation,
                                                                power, max)
            else:
                user._HCNav.setPositionFactors(component, attenuation,
                                                                power, max)

        def setOrientationFactors(self, attenuation, power, max=1.0,
                                                                    user=None):
                                                        # should be a vector
            if hasattr(self, '_local'):
                self._local.setOrientationFactors(attenuation, power, max)
                return
            if user is None:
                for user_name, user in self.BlenderVR.getAllUsers().items():
                    user._HCNav.setOrientationFactors(attenuation, power, max)
            else:
                user._HCNav.setOrientationFactors(attenuation, power, max)

        def setHeadNeckLocation(self, location, user=None):
            if hasattr(self, '_local'):
                self._local.setHeadNeckLocation(location)
                return
            if user is None:
                for user_name, user in self.BlenderVR.getAllUsers().items():
                    user._HCNav.setHeadNeckLocation(location)
            else:
                user._HCNav.setHeadNeckLocation(location)

        def update(self, state, user=None):
            if hasattr(self, '_local'):
                self._local.update(state)
                return
            if user is None:
                for user_name, user in self.BlenderVR.getAllUsers().items():
                    user._HCNav.update(state)
            else:
                user._HCNav.update(state)
            self.sendToConsole(self._interactor_name, self.getNavigationState())

        def setHeadLocation(self, user, info):
            """Update the viewer location based on the tracker position.

            :param user: who is using this head tracker
            :type user: :class:`blendervr.player.user.User`
            :param info: data from the tracker device
            :type info: dict with 'matrix' (a 4x4 :class:`mathutils.Matrix`)
            """
            if hasattr(self, '_local'):
                self._local.setHeadLocation(info['matrix'], info)
                return
            user._HCNav.setHeadLocation(info['matrix'], info)

        def getNavigationState(self):
            for user_name, user in self.BlenderVR.getAllUsers().items():
                if user._HCNav.getNavigationState():
                    return True
            return False

        def receivedFromConsole(self, command, argument):
            if command != self._interactor_name:
                return False

            if self._default_user:
                if argument == 'start':
                    self.update(self.START, self._default_user)
                elif argument == 'stop':
                    self.update(self.STOP, self._default_user)
                elif argument == 'calibration':
                    self.update(self.CALIBRATE, self._default_user)
                elif argument == 'home':
                    self.update(self.RESET, self._default_user)

            return True
elif is_console():

    from ..tools.gui.qt import QtGui

    class HCNav(Interactor):
        def __init__(self, parent):
            Interactor.__init__(self, parent)

            self._interactor_name = COMMON_NAME

            self._widget = QtGui.QWidget()
            from ..tools import gui, getModulePath
            self._ui = gui.load(os.path.join(getModulePath(), 'designer',
                            'head_controlled_navigation.ui'), self._widget)
            self._ui.navigation.clicked.connect(self.cb_navigation)
            self._ui.calibration.clicked.connect(self.cb_calibration)
            self._ui.home.clicked.connect(self.cb_home)

        def registerWidget(self, parent_widget):
            from ..tools.gui import insertWidgetInsideAnother
            insertWidgetInsideAnother(parent_widget, self._widget)

        def cb_navigation(self):
            if self._ui.navigation.isChecked():
                self.sendToVirtualEnvironment(self._interactor_name, 'start')
            else:
                self.sendToVirtualEnvironment(self._interactor_name, 'stop')

        def cb_calibration(self):
            self.sendToVirtualEnvironment(self._interactor_name, 'calibration')

        def cb_home(self):
            self.sendToVirtualEnvironment(self._interactor_name, 'home')

        def receivedFromVirtualEnvironment(self, command, argument):
            if self._interactor_name != command:
                return False
            self._ui.navigation.setChecked(argument)
            return True
