# -*- coding: utf-8 -*-
# file: blendervr/plugins/oculus_dk2/virtual_environment/__init__.py

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
from . import user


class OculusDK2(base.Base):
    def __init__(self, parent, configuration):
        super(OculusDK2, self).__init__(parent)

        self._user = None
        self._hmd = None
        self._description = None
        self._matrix = None

        self.checkLibraryPath()

        try:
            from oculusvr import Hmd
            assert(Hmd)

        except ImportError:
            self.logger.info('Oculus DK2 plugin error: no \"oculusvr\" module available. Make sure you have the projec submodules. Please refer to the BlenderVR documentation')
            self._available = False
            return

        except Exception as err:
            self.logger.error(err)
            self._available = False
            return

        if 'users' in configuration:
            for user_entry in configuration['users']:
                try:
                    _user = user.User(self, user_entry)
                    if _user.isAvailable():
                        viewer = _user.getUser()
                        if viewer is not None:
                            self._user = _user
                            # each computer can only have one user/viewer
                            break
                except:
                    self.logger.log_traceback(False)

        self._available = True

    def start(self):
        super(OculusDK2, self).start()
        from mathutils import Matrix

        try:
            self._matrix = Matrix.Identity(4)
            self._startOculus()
        except Exception:
            self._available = False

    def run(self):
        super(OculusDK2, self).run()

        try:
            self._updateMatrix()
            info = {'matrix' : self._matrix}
            self._user.run(info)

        except Exception as err:
            self.logger.log_traceback(err)

    def _updateMatrix(self):
        try:
            matrix = self._getMatrix()
            if matrix:
                self._matrix = matrix
        except Exception as err:
            self.logger.log_traceback(err)

    def checkMethods(self):
        if not self._available:
            self.logger.info('Oculus DK2 python module not available !')
            return False

        if not self._user:
            self.logger.info('Oculus DK2 python module not available ! No valid user found for this computer.')
            return False

        if not self._user.checkMethod(True):
            self.logger.info('No Oculus DK2 processor method available !')
            del self._user
            self._user = None
            return False

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

    def _startOculus(self):
        from oculusvr import (
                Hmd,
                cast,
                POINTER,
                ovrHmdDesc,
                ovrVector3f,
                )

        try:
            Hmd.initialize()
        except SystemError as err:
            self.logger.error("Oculus initialization failed, check the physical connections and run again")

        if Hmd.detect() == 1:
            self._hmd = Hmd()
            self._description = cast(self._hmd.hmd, POINTER(ovrHmdDesc)).contents
            self._frame = 0
            self._eyes_offset = [ ovrVector3f(), ovrVector3f() ]
            self._eyes_offset[0] = 0.0, 0.0, 0.0
            self._eyes_offset[1] = 0.0, 0.0, 0.0

            self._hmd.configure_tracking()
            self.logger.info(self._description.ProductName)

        else:
            self.logger.error("Oculus not connected")
            raise Exception

    def _getMatrix(self):
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
