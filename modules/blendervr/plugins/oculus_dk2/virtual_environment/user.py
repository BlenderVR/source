# -*- coding: utf-8 -*-
# file: blendervr/plugins/oculus_dk2/virtual_environment/user.py

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

from .. import base
from ....player import device


class User(device.Sender):
    def __init__(self, parent, configuration):
        _configuration = configuration.copy()
        _configuration['users'] = _configuration['viewer']

        self._oculus = Oculus(parent)
        self._matrix = None

        super(User, self).__init__(parent, _configuration)
        self._viewer = self.BlenderVR.getUserByName(configuration['viewer'])
        self._available = True

    def run(self):
        if self._available:
            try:
                self._updateMatrix()
                info = {'matrix' : self._matrix}
                self.process(info)
            except Exception as err:
                self.logger.log_traceback(err)

    def getName(self):
        return self._viewer.getName()

    def getUser(self):
        return self._viewer

    def isAvailable(self):
        return self._available

    def start(self):
        from mathutils import Matrix
        try:
            self._matrix = Matrix.Identity(4)
            self._oculus.start()
        except Exception:
            self._available = False

    def _updateMatrix(self):
        from mathutils import Quaternion, Matrix

        try:
            matrix = self._oculus.getMatrix()
            if matrix:
                self._matrix = matrix
        except Exception as err:
            self.logger.log_traceback(err)


class Oculus(base.Base):
    def __init__(self, parent):
        super(Oculus, self).__init__(parent)

        self._hmd = None
        self._description = None

    def start(self):
        from oculusvr import (
                Hmd,
                cast,
                POINTER,
                )

        try:
            Hmd.initialize()
        except SystemError as err:
            self.logger.error("Oculus initialization failed, check the physical connections and run again")

        if Hmd.detect() == 1:
            self._hmd = Hmd()
            self._description = cast(self._hmd.hmd, POINTER(ovrHmdDesc)).contents
            self._frame = 0
            self._eye_offset = [ [0.0, 0.0, 0.0], [0.0, 0.0, 0.0] ]
            self._hmd.configure_tracking()

            self.logger.info(self._description.ProductName)

        else:
            self.logger.error("Oculus not connected")
            raise Exception

    def getMatrix(self):
        from oculusvr import Hmd
        from mathutils import (
                Quaternion,
                Matrix,
                )

        if self._hmd and Hmd.detect() == 1:
            self._frame += 1

            poses = self._hmd.get_eye_poses(self._frame, self._eyes_offset)

            # oculus may be returning the matrix for both eyes
            # but we are using a single eye without offset

            rotation_raw = poses[0].Orientation.toList()
            position_raw = poses[0].Position.toList()

            rotation = Quaternion(rotation_raw).to_matrix().to_4x4()
            position = Matrix.Translation(position_raw)

            matrix = position * rotation
            matrix.invert()

            return matrix
        return None
