# -*- coding: utf-8 -*-
# file: blendervr/player/screen/planovision.py

## Copyright (C) LIMSI-CNRS (2015)
##
## contributor(s) : BlenderVR Development Team
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
from . import base
from .. import exceptions

from mathutils import Matrix, Vector

""" @package planovision
Manager of planvision screens with BlenderVR ...
"""


class Device(base.Base):

    def __init__(self, parent, configuration):
        super(Device, self).__init__(parent, configuration)

        self._screen_informations = self.computeScreenRegardingCorners(
                            configuration['planovision']['corners'])

    def _updateMatrixForBuffer(self, bufferName, camera, depth):

        user = self._buffers[bufferName]['user']
        vehicle_scale = self.BlenderVR.scale

        # Then, we transfer from the Camera referenceFrame (ie. : vehicle one)
        # to local screen reference frame
        localScreenInCameraReferenceFrame = \
                self._screen_informations['fromScreensOriginToLocalScreen']

        userPositionInCameraReferenceFrame = user.getPosition()
        userEyeSeparation = user.getEyeSeparation()
        eyePositionInUserReferenceFrame = mathutils.Vector((
                    self._buffers[bufferName]['eye']
                    * userEyeSeparation / 2.0, 0.0, 0.0, 1.0))

        viewPointPositionInScreenReferenceFrame = \
                    localScreenInCameraReferenceFrame \
                    * userPositionInCameraReferenceFrame \
                    * eyePositionInUserReferenceFrame

        viewPointPositionInScreenReferenceFrame.resize_3d()

        head_position = userPositionInCameraReferenceFrame.translation

        # in the planovision the eyes are always looking at the middle of the table
        xy = Vector((head_position[0], head_position[1], 0.0))
        Pv = xy.cross(Vector((0.0, 0.0, 1.0))) # perpendicular of xy
        Pv.normalize()
        Pv *= self._buffers[bufferName]['eye'] * userEyeSeparation * 0.5
        eye_position = xy - Pv

        viewPointPositionInScreenReferenceFrame = (eye_position[0], eye_position[1], head_position[2])

        nearVal = camera.near
        farVal = camera.far

        horizontalShifting = viewPointPositionInScreenReferenceFrame[0]
        verticalShifting = viewPointPositionInScreenReferenceFrame[1]
        depthShifting = viewPointPositionInScreenReferenceFrame[2]

        if (depthShifting >= 0.0001) or (depthShifting <= -0.0001):
            depthPlaneRatio = nearVal / depthShifting
        else:
            depthPlaneRatio = nearVal

        left = (self._screen_informations['windowCoordinates']['left']
                    - horizontalShifting) * depthPlaneRatio
        right = (self._screen_informations['windowCoordinates']['right']
                    - horizontalShifting) * depthPlaneRatio
        bottom = (self._screen_informations['windowCoordinates']['bottom']
                    - verticalShifting) * depthPlaneRatio
        top = (self._screen_informations['windowCoordinates']['top']
                    - verticalShifting) * depthPlaneRatio

        projection_matrix = mathutils.Matrix()
        projection_matrix[0][0] = 2 * nearVal / (right - left)
        projection_matrix[0][2] = (right + left) / (right - left)

        projection_matrix[1][1] = 2 * nearVal / (top - bottom)
        projection_matrix[1][2] = (top + bottom) / (top - bottom)

        projection_matrix[2][2] = - (farVal + nearVal) / (farVal - nearVal)
        projection_matrix[2][3] = - 2 * farVal * nearVal / (farVal - nearVal)

        projection_matrix[3][2] = - 1.0
        projection_matrix[3][3] = 0.0

        world_translation = Matrix.Translation(camera.worldPosition)
        modelview_matrix = world_translation * Matrix.Translation(Vector((horizontalShifting, verticalShifting, depthShifting)) * vehicle_scale)
        modelview_matrix = user.getVehiclePosition() * modelview_matrix
        modelview_matrix.invert()

        self._setModelViewMatrix(modelview_matrix)
        self._setProjectionMatrix(projection_matrix)
