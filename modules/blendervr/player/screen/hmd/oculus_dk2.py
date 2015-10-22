# -*- coding: utf-8 -*-
# file: blendervr/player/screen/hmd/oculus_dk2.py

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
from mathutils import Matrix, Quaternion

import bge
from . import base
from ... import exceptions

""" @package hmd
Manager of Oculus DK2 screens with BlenderVR
"""

warning_for_unsure_projection_displayed = False

class Device(base.Device):

    def __init__(self, parent, configuration):
        super(Device, self).__init__(parent, configuration)
        self._plugin = None
        self._modelview_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._projection_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._near = -1
        self._far = -1

        self.checkLibraryPath()

        try:
            from oculusvr import Hmd
            assert(Hmd)

        except ImportError:
            self.logger.info('Oculus DK2 plugin error: no \"oculusvr\" module available. Make sure you have the project submodules. Please refer to the BlenderVR documentation')
            return

        except Exception as err:
            self.logger.error(err)
            self._available = False
            return

    def start(self):
        super(Device, self).start()

        import sys

        self._plugin = self.BlenderVR.getPlugin('oculus_dk2')
        if self._plugin is None:
            self.logger.error("Oculus DK2 plugin (oculus_dk2) not setup in the configuration file, HMD device won't work")
            #self.BlenderVR.quit("Oculus DK2 plugin (oculus_dk2) not setup in the configuration file, HMD device won't work")
            return

        try:
            import bge

            width = bge.render.getWindowWidth()
            height = bge.render.getWindowHeight()

            cont = bge.logic.getCurrentController()

            cont.owner["screen_width"] = width
            cont.owner["screen_height"] = height

            ELEMENTS_MAIN_PREFIX = 'BlenderVR:'
            ACTUATOR = ELEMENTS_MAIN_PREFIX + 'OculusDK2:Filter'

            actuator = cont.actuators.get(ACTUATOR)
            if not actuator:
                self.logger.error('Error: Oculus DK2 2D Filter Actuator not found ({0})'.format(ACTUATOR))
            else:
                cont.activate(actuator)

        except Exception as err:
            self.logger.error(err)

    def _updateMatrixForBuffer(self, bufferName, camera, depth):

        scale = self.BlenderVR.scale
        user = self._buffers[bufferName]['user']

        if bufferName == 'left':
            near = camera.near * scale
            far = camera.far * scale

            self._updateProjectionMatrix(near, far)
            self._updateModelViewMatrix(user.getPosition() * user.getVehiclePosition(), camera.modelview_matrix)

            self._setModelViewMatrix(self._modelview_matrix[0])
            self._setProjectionMatrix(self._projection_matrix[0])
        else:
            self._setModelViewMatrix(self._modelview_matrix[1])
            self._setProjectionMatrix(self._projection_matrix[1])


    def _updateModelViewMatrix(self, user_matrix, camera_matrix):
        from oculusvr import Hmd
        from bge import logic

        global_dict = logic.globalDict
        hmd = global_dict.get('hmd')

        if hmd and Hmd.detect() == 1:
            global_dict['frame'] += 1

            frame = global_dict['frame']
            fov_ports = global_dict['fovPorts']
            eye_offsets = global_dict['eyeOffsets']

            poses = hmd.get_eye_poses(frame, eye_offsets)
            hmd.begin_frame(frame)

            orientation = [None, None]
            position = [None, None]

            for eye in range(2):
                orientation_raw = poses[eye].Orientation.toList()
                position_raw = poses[eye].Position.toList()

                orientation = Quaternion(orientation_raw).to_matrix().to_4x4()
                position = Matrix.Translation(position_raw)

                matrix = position * orientation
                matrix.invert()

                self._modelview_matrix[eye] = self._convertMatrixTo4x4(user_matrix * matrix * camera_matrix)

    def _convertMatrixTo4x4(self, value):
        matrix = Matrix()

        matrix[0] = value[0:4]
        matrix[1] = value[4:8]
        matrix[2] = value[8:12]
        matrix[3] = value[12:16]

        return matrix.transposed()


    def _updateProjectionMatrix(self, near, far):

        if not self._cameraClippingChanged(near, far):
            return

        from bge import logic
        import oculusvr as ovr

        global_dict = logic.globalDict
        fov_ports = global_dict['fovPorts']

        self._projection_matrix[0] = self._convertMatrixTo4x4(ovr.Hmd.get_perspective(fov_ports[0], near, far, True).toList())
        self._projection_matrix[1] = self._convertMatrixTo4x4(ovr.Hmd.get_perspective(fov_ports[1], near, far, True).toList())

    def _cameraClippingChanged(self, near, far):
        """
        check if near of far values changed
        """
        if near == self._near and far == self._far:
            return False

        self._near = near
        self._far = far

        return True

    def checkLibraryPath(self):
        """if library exists append it to sys.path"""
        import sys
        import os
        from .... import tools

        libs_path = tools.getLibsPath()
        oculus_path = os.path.join(libs_path, "python-ovrsdk")

        if oculus_path not in sys.path:
            sys.path.append(oculus_path)

