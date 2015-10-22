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
        self._modelview_matrix = [None, None]
        self._projection_matrix = [None, None]
        self._near = -100.0
        self._far = -100.0

        self.checkLibraryPath()

        try:
            from oculusvr import Hmd
            assert(Hmd)

        except ImportError:
            self.logger.info('Oculus DK2 plugin error: no \"oculusvr\" module available. Make sure you have the project submodules. Please refer to the BlenderVR documentation')
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

        self.logger.debug("START PLUGIN")

        try:
            self._startOculus()

        except Exception:
            self._available = False

    def run(self):
        super(OculusDK2, self).run()

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
        from time import sleep
        import oculusvr as ovr
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

        """
        self._hmd = Hmd()
        self._description = cast(self._hmd.hmd, POINTER(ovrHmdDesc)).contents
        self._frame = 0
        self._eyes_offset = [ ovrVector3f(), ovrVector3f() ]
        self._eyes_offset[0] = 0.0, 0.0, 0.0
        self._eyes_offset[1] = 0.0, 0.0, 0.0

        self._hmd.configure_tracking()
        self.logger.info(self._description.ProductName)
        """

        try:
            debug = not Hmd.detect()

            if debug:
                self.logger.error("Oculus not connected")

            try:
                self._hmd = Hmd()
            except:
                self._hmd = Hmd(debug=True)

            desc = self._hmd.hmd.contents
            self._frame = -1

            sleep(0.1)
            self._hmd.configure_tracking()

            self._fovPorts = (
                desc.DefaultEyeFov[0],
                desc.DefaultEyeFov[1],
                )

            #self._eyeTextures = [ ovrGLTexture(), ovrGLTexture() ]
            self._eyeOffsets = [ ovrVector3f(), ovrVector3f() ]
            self._width = [-1, -1]
            self._height = [-1, -1]

            rc = ovr.ovrRenderAPIConfig()
            header = rc.Header
            header.API = ovr.ovrRenderAPI_OpenGL
            header.BackBufferSize = desc.Resolution
            header.Multisample = 1

            for i in range(8):
                rc.PlatformData[i] = 0

            self._eyeRenderDescs = self._hmd.configure_rendering(rc, self._fovPorts)

            for eye in range(2):
                size = self._hmd.get_fov_texture_size(eye, self._fovPorts[eye])
                self._width[eye], self._height[eye] = size.w, size.h
                #eyeTexture = self._eyeTextures[eye]
                #eyeTexture.API = ovr.ovrRenderAPI_OpenGL
                #header = eyeTexture.Texture.Header
                #header.TextureSize = size
                #vp = header.RenderViewport
                #vp.Size = size
                #vp.Pos.x = 0
                #vp.Pos.y = 0

                self._eyeOffsets[eye] = self._eyeRenderDescs[eye].HmdToEyeViewOffset


            # store the data globally, to access it in screen
            from bge import logic
            global_dict = logic.globalDict

            global_dict['hmd'] = self._hmd
            global_dict['frame'] = self._frame
            global_dict['eyeOffsets'] = self._eyeOffsets
            global_dict['fovPorts'] = self._fovPorts

        except Exception as err:
            self.logger.error("Error initializing Oculus", str(err))
        else:
            self.logger.info("Oculus properly initialized")
