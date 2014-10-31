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

MOUSE_RESCALE_FOR_ARCBALLS = 1000

if is_virtual_environment():

    import bge, mathutils, math
    from ..player import device
    from ..player import keyboardAndMouse
    from .arc_ball import ArcBall

    class ViewPoint(Interactor):
        def __init__(self, parent):
            Interactor.__init__(self, parent)
            self._activated = False
            users           = self.blenderVR.getScreenUsers()
            if self.blenderVR.isMaster() and (len(users) == 1):
                self._user         = users[0]
                self._window       = (bge.render.getWindowWidth(), bge.render.getWindowHeight())
                self._arcBall      = ArcBall(self, self._window[0], self._window[1])
                self._scale        = 1.0
                self._delta        = None
                self._arcBall.setOrientation(False)

        def activation(self, activate):
            if hasattr(self, '_user'):
                self._activated = activate
                bge.render.showMouse(self._activated)

        def isActivated(self):
            return self._activated

        @property
        def viewpointScale(self):
            return self._scale

        @viewpointScale.setter
        def viewpointScale(self, scale):
            self._scale = scale

        def _amplifier(value):
            return math.pow(4.0 * value, 3.0)

        def keyboardAndMouse(self, info):
            if keyboardAndMouse.WIDTH in info:
                self._arcBall.setBounds(info[keyboardAndMouse.WIDTH], info[keyboardAndMouse.HEIGHT])
                
            if self.isActivated() and (keyboardAndMouse.MOUSE_POSITION in info):

                mousePosition = info[keyboardAndMouse.MOUSE_POSITION]

                # Manage rotation (arc balls)
                if info[keyboardAndMouse.BUTTON_LEFT] == device.STATE_PRESS:
                    self._userPosition = self._user.getVehiclePosition(True)
                    self._arcBall.click(mousePosition)
                    return True
                elif info[keyboardAndMouse.BUTTON_LEFT] == device.STATE_ACTIVE:
                    update = mathutils.Matrix(self._arcBall.drag(mousePosition))
                    self._user.setVehiclePosition(update.to_4x4().inverted() * self._userPosition)
                    return True
                elif info[keyboardAndMouse.BUTTON_LEFT] == device.STATE_RELEASE:
                    return True


                if (info[keyboardAndMouse.BUTTON_MIDDLE] == device.STATE_PRESS) or (info[keyboardAndMouse.BUTTON_RIGHT] == device.STATE_PRESS) :
                    bge.render.setMousePosition(int(bge.render.getWindowWidth() / 2), int(bge.render.getWindowHeight() / 2))
                    return True
                elif info[keyboardAndMouse.BUTTON_MIDDLE] == device.STATE_ACTIVE:
                    x = ViewPoint._amplifier(0.5 - mousePosition[0])
                    y = ViewPoint._amplifier(mousePosition[1] - 0.5)
                    self._delta  = mathutils.Vector((x, y, 0)) * self._scale
                    return True
                elif info[keyboardAndMouse.BUTTON_RIGHT] == device.STATE_ACTIVE:
                    z = ViewPoint._amplifier(0.5 - mousePosition[1])
                    self._delta  = mathutils.Vector((0, 0, z)) * self._scale
                    return True
                elif (info[keyboardAndMouse.BUTTON_MIDDLE] == device.STATE_RELEASE) or (info[keyboardAndMouse.BUTTON_RIGHT] == device.STATE_RELEASE):
                    self._delta = None
                    return True
            return Interactor.keyboardAndMouse(self, info)

        def run(self):
            try:
                if self._delta:
                    self._user.setVehiclePosition(mathutils.Matrix.Translation(self._delta) * self._user.getVehiclePosition(True))
            except:
                pass
