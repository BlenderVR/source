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

from ... import *
from .. import Interactor
from ...tools import protocol

PRESS_EVENT   = 'press'
MOVE_EVENT    = 'move'
RELEASE_EVENT = 'release'
COMMON_NAME   = 'update arcballs'

if is_virtual_environment():
    import copy, mathutils
    import bge
    from ...player.user import User
    from ...player import device
    from ...player import keyboardAndMouse

    class Console(Interactor):

        def __init__(self, parent, name = COMMON_NAME):
            Interactor.__init__(self, parent)
            self._name           = name
            self._object         = None
            self._objectPosition = mathutils.Matrix()
            self._grabbed        = False
            users                = self.blenderVR.getScreenUsers()

        def selectObject(self, _object):
            if not self._grabbed:
                self._object = _object

        def receivedFromConsole(self, command, argument):
            if command != self._name:
                return False
            command, argument = protocol.decomposeMessage(argument)
            if command == PRESS_EVENT:
                if isinstance(self._object, bge.types.KX_GameObject):
                    self._objectPosition = copy.copy(self._object.localTransform)
                    self._grabbed = True
                elif isinstance(self._object, User):
                    self._objectPosition = self._object.getVehiclePosition(True)
                    self._grabbed = True
            else:
                if isinstance(self._object, bge.types.KX_GameObject):
                    self._object.localTransform = self._objectPosition * mathutils.Matrix(argument).to_4x4()
                if isinstance(self._object, User):
                    self._object.setVehiclePosition(mathutils.Matrix(argument).to_4x4().inverted() * self._objectPosition)
                if command == RELEASE_EVENT:
                    self._grabbed = False
            return True

elif is_console():
    import bge
    from . import ArcBall, removeScale
    from ...tools.gui.qt import QtCore, QtOpenGL, QtGui

    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy, os

    class Console(Interactor, QtOpenGL.QGLWidget):

        def __init__(self, parent, name = COMMON_NAME):
            Interactor.__init__(self, parent)
            QtOpenGL.QGLWidget.__init__(self)

            self._name = name

            geometry = self.geometry()
            self._arcBall = ArcBall(geometry.width(), geometry.height())

            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
            self.setSizePolicy(sizePolicy)

            self.start()

            from ..wavefront_obj import Reader
            from ...tools import getModulePath
            self._suzanne = Reader(os.path.join(getModulePath(), 'suzanne.obj'))

            # Under MACOS X, QtCore.Qt.MouseButton.LeftButton is not defined ! So we use 1 as button
            try:
                self._active_button = QtCore.Qt.MouseButton.LeftButton
            except:
                self._active_button = 1

        def registerWidget(self, parent_widget):
            from ...tools.gui import insertWidgetInsideAnother
            insertWidgetInsideAnother(parent_widget, self)

        def start(self):
            self._draging = False
            self._startOrientation   = numpy.identity(3)
            self._currentOrientation = self._startOrientation
            self._transformation     = numpy.identity(4)

        def initializeGL(self):
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glEnable (GL_DEPTH_TEST)
            glEnable (GL_POLYGON_SMOOTH)
            self.setOrientation(False)

        def setOrientation(self, object):
            if object:
                self._lookWorld = False
                glEnable(GL_LIGHTING)
                glEnable(GL_LIGHT0)
                glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0))
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
            else:
                self._lookWorld = True
                glDisable(GL_LIGHTING)
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                glFrustum(-1, 1, -1, 1, 1, 1000.0)

            glMatrixMode(GL_MODELVIEW)

            self._arcBall.setOrientation(not self._lookWorld)

        def mousePressEvent(self, event):
            if event.button() == self._active_button:
                self._arcBall.click((event.x(), event.y()))
                self._draging = True
                self.sendToVirtualEnvironment(self._name, protocol.composeMessage(PRESS_EVENT))
            QtOpenGL.QGLWidget.mousePressEvent(self, event)

        def mouseMoveEvent(self, event):
            if self._draging:
                update = self._arcBall.drag((event.x(), event.y()))
                self._currentOrientation = self._startOrientation.dot(update)
                self.updateGL()
                self.sendToVirtualEnvironment(self._name, protocol.composeMessage(MOVE_EVENT, update.tolist()))
            QtOpenGL.QGLWidget.mouseMoveEvent(self, event)

        def mouseReleaseEvent(self, event):
            if event.button() == self._active_button:
                update = self._arcBall.drag((event.x(), event.y()))
                self._startOrientation = removeScale(self._startOrientation.dot(update))
                self.sendToVirtualEnvironment(self._name, protocol.composeMessage(RELEASE_EVENT, update.tolist()))
                self._draging = False
            QtOpenGL.QGLWidget.mouseReleaseEvent(self, event)

        def resizeGL(self, width, height):
            if height == 0:
                height = 1
            self._arcBall.setBounds(width, height)
            glViewport(0, 0, width, height)
            QtOpenGL.QGLWidget.resizeGL(self, width, height)

        def paintGL(self):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self._transformation [0:3,0:3] = self._currentOrientation

            glLoadIdentity()
            glMultMatrixf(self._transformation)

            if self._lookWorld:
                quadric = gluNewQuadric()
                gluSphere(quadric, 100.0, 50, 50)
                gluDeleteQuadric(quadric)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5)) 
                glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0))
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.7, 0.0, 0.0))
                self._suzanne.draw()
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.0, 0.0, 0.7))
                glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.3, 0.3, 0.7))
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                quadric = gluNewQuadric()
                gluSphere(quadric, 1.0, 10, 10)
                gluDeleteQuadric(quadric)
