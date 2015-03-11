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
        self._websocket = None
        self._matrix = None

        try:
            from websocket import create_connection
            assert(create_connection)

        except ImportError:
            self.logger.info('Oculus DK2 plugin error: no websocket module available. Please refer to the Blender-VR documentation')
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
        try:
            from websocket import create_connection
            from mathutils import Matrix

            self._websocket = create_connection("ws://localhost:8888/")
            self._matrix = Matrix.Identity(4)

        except Exception as err:
            self.logger.log_traceback(err)

    def run(self):
        super(OculusDK2, self).run()

        try:
            self._updateMatrix()
            info = {'matrix' : self._matrix}
            self._user.run(info)

        except Exception as err:
            self.logger.log_traceback(err)

    def _updateMatrix(self):
        from mathutils import Quaternion, Matrix
        import json


        try:
            self._websocket.send('n')
            result = json.loads(self._websocket.recv())

            self._matrix = Quaternion((result[7],
                                       result[4],
                                       result[5],
                                       result[6])).to_matrix().to_4x4()

            position = Matrix.Translation((result[1], result[2], result[3]))
            self._matrix = position * self._matrix

            self._matrix.invert()

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
