# -*- coding: utf-8 -*-
# file: blendervr/plugins/occulus_rift/virtual_environment/__init__.py

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
from ....player import device, exceptions
from . import user


class OcculusRift(base.Base, device.Sender):
    def __init__(self, parent, configuration):
        super(OcculusRift, self).__init__(parent)

        self._viewers = {}
        self._users = {}

        if 'users' in configuration:
            for index, user_entry in enumerate(configuration['users']):
                try:
                    _user = user.User(self, user_entry, index)

                    if _user.isAvailable():
                        self._users[_user.getName()] = _user
                        viewer = _user.getUser()

                        if viewer is not None:
                            self._viewers[id(viewer)] = _user
                except:
                    self.logger.log_traceback(False)

        try:
            from game_engine_rift.rift import PyRift
            assert PyRift     # avoid import unused

        except ImportError:
            self.logger.info('No Occulus Rift python module available')
            self._available = False
            return

        except Exception as err:
            self.logger.error(err)
            self._available = False
            return

        self._available = True

    def isAvailable(self):
        if not self._available:
            self.logger.info('Occulus Rift python module not available !')
            return False
        elif not self._viewers:
            self.logger.info('Occulus Rift python module not available ! No valid user found.')
            return False
        return True

    """
    TODO
    call the processor methods with the info['matrix']
    """
    def run(self):

        """
        do the following for a user only
        """
        try:
            import bge
            from mathutils import Euler
            from math import pi

            from game_engine_rift.rift import PyRift

            if not hasattr(bge.logic, 'rift'):
                bge.logic.rift = PyRift()
                euler = Euler((0, 0, 0), 'XYZ')
            else:
                self._poll(bge.logic.rift)
                euler = bge.logic.rotation.to_euler()

            """
            TODO: the following is the part we need to change later
            so it uses our internal classes to access the navigation
            (instead of by passing it entirely)
            """
            scene = bge.logic.getCurrentScene()
            camera = scene.active_camera
            fix = Euler((-pi/2, 0, 0), 'XYZ')

            rot = Euler((-euler.z, euler.y, -euler.x), 'XYZ')
            rot.rotate(fix)
            camera.worldOrientation = rot

        except Exception as err:
            self.logger.error(err)

    def _poll(self, rift):
        import bge
        from mathutils import Quaternion

        rift.poll()
        bge.logic.rotation = Quaternion((rift.rotation[0],
                rift.rotation[1],
                rift.rotation[2],
                rift.rotation[3]))

