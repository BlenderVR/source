# -*- coding: utf-8 -*-
# file: blendervr/player/screen/base.py

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

import mathutils
import bge
from .. import base
from .. import exceptions
import bgl

LEFT_EYE = bge.render.LEFT_EYE
RIGHT_EYE = bge.render.RIGHT_EYE

class Base(base.Base):
    def __init__(self, parent, configuration):
        base.Base.__init__(self, parent)

        try:
            if configuration['viewport'] is not None:
                self._viewport = configuration['viewport']
        except:
            pass

        self._focus = configuration['keep_focus']
        if self._focus:
            self.logger.info('Focus forced on this screen')

        buffers = configuration['graphic_buffer']
        self._buffers = {}
        self._users = []
        for information in buffers:
            user = self.blenderVR.getUserByName(information['user'])
            if user not in self._users:
                self._users.append(user)
            if information['eye'] == 'left':
                eye = -1.0
            elif information['eye'] == 'right':
                eye = 1.0
            else:
                eye = 0
            self._buffers[information['buffer']] = {'user': user, 'eye': eye}

        stereo_mode = bgl.Buffer(bgl.GL_BYTE, 1)
        bgl.glGetBooleanv(bgl.GL_STEREO, stereo_mode)
        if ((not 'left' in self._buffers) or (not 'right' in self._buffers)) \
                and (stereo_mode == 1):
            raise exceptions.VirtualEnvironment('Stereo window but buffer '
                                                'is missing !')
        if (not 'middle' in self._buffers) and (stereo_mode == 0):
            raise exceptions.VirtualEnvironment('Monoscopic window but '
                                            '"middle" buffer is missing !')

    def getBufferUser(self, bufferName):
        if bufferName in self._buffers:
            return self._buffers[bufferName]['user']
        return None

    def start(self):
        pass

    def run(self):
        try:
            # Force the window to keep the focus by setting mouse position
            # in the middle of the window ...
            if self._focus:
                bge.render.setMousePosition(bge.render.getWindowWidth() // 2,
                                            bge.render.getWindowHeight() // 2)

            scene = bge.logic.getCurrentScene()
            camera = scene.active_camera

            if hasattr(self, '_viewport'):
                camera.useViewport = True
                camera.setViewport(self._viewport[0], self._viewport[1],
                                   self._viewport[2], self._viewport[3])
            else:
                camera.useViewport = False

            depth = (camera.near + camera.far) / 2.0

            stereo_eye = bge.render.getStereoEye()

            if 'left' in self._buffers and stereo_eye == LEFT_EYE:
                self._updateMatrixForBuffer('left', camera, depth)

            elif 'right' in self._buffers and stereo_eye == RIGHT_EYE:
                self._updateMatrixForBuffer('right', camera, depth)

            elif 'mono' in self._buffers:
                self._updateMatrixForBuffer('mono', camera, depth)

        except:
            self.blenderVR.stopDueToError()

    def getUsers(self):
        return self._users

    def computeScreenRegardingCorners(self, configuration):
        corners = {}
        for name, corner in configuration.items():
            corners[name] = mathutils.Vector(tuple(corner))

        # First, check corners validity !
        XVector = corners['topRightCorner'] - corners['topLeftCorner']
        if XVector.length < (corners['topRightCorner'][0] / 100000):
            raise exceptions.VirtualEnvironment("top right and left corners"
                                                " are same points !")
            return

        YVector = corners['topRightCorner'] - corners['bottomRightCorner']
        if YVector.length < (corners['topRightCorner'][0] / 100000):
            raise exceptions.VirtualEnvironment("top and bottom right corners"
                                                " are same points !")
            return

        ZVector = XVector.cross(YVector)
        if ZVector.length < (corners['topRightCorner'][0] / 100000):
            raise exceptions.VirtualEnvironment("Three corners are not "
                                                "perpendicular !")
            return
        corners['bottomLeftCorner'] = corners['topLeftCorner'] - YVector

        Center = (corners['bottomLeftCorner']
                  + corners['topRightCorner']) / 2.0

        XVector.normalize()
        YVector.normalize()
        ZVector.normalize()

        result = {}

        #TODO: we normally dont need to store the matrix into result here
        # as it is overriden ar multiply operation when storing into
        # result['fromScreensOriginToLocalScreen'] again.
        result['fromScreensOriginToLocalScreen'] = mathutils.Matrix()
        scmat = result['fromScreensOriginToLocalScreen']    # shortcut
        scmat[0][0] = XVector[0]
        scmat[1][0] = XVector[1]
        scmat[2][0] = XVector[2]

        scmat[0][1] = YVector[0]
        scmat[1][1] = YVector[1]
        scmat[2][1] = YVector[2]

        scmat[0][2] = ZVector[0]
        scmat[1][2] = ZVector[1]
        scmat[2][2] = ZVector[2]

        scmat.invert()

        result['fromScreensOriginToLocalScreen'] = scmat \
                            * mathutils.Matrix.Translation((-Center))

        result['cornersLocally'] = {}
        for key, value in corners.items():
            corners[key].resize_4d()
            result['cornersLocally'][key] = \
                    result['fromScreensOriginToLocalScreen'] * corners[key]

        wc = {}    # shortcut
        wc['left'] = result['cornersLocally']['topLeftCorner'][0]
        wc['right'] = result['cornersLocally']['topRightCorner'][0]
        wc['top'] = result['cornersLocally']['topRightCorner'][1]
        wc['bottom'] = result['cornersLocally']['bottomRightCorner'][1]
        result['windowCoordinates'] = wc

        return result

    def _setModelViewMatrix(self, camera, matrix):
        from bgl import (
                Buffer,
                GL_FLOAT,
                GL_MODELVIEW,
                glMatrixMode,
                glLoadMatrixf,
                )

        matrix *= camera.modelview_matrix
        buf = Buffer(GL_FLOAT, [4, 4])
        for i in range(4):
            for j in range(4):
                # transposed
                buf[i][j] = matrix[j][i]

        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(buf)

    def _setProjectionMatrix(self, camera, matrix):
        camera.projection_matrix = matrix
