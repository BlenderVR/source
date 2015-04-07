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

        self._devices = []

        try:
            from websocket import create_connection
            assert(create_connection)

        except ImportError:
            self.logger.info('Oculus DK2 plugin error: no websocket module available. Please refer to the BlenderVR documentation')
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
                            self._devices.append(_user)
                except:
                    self.logger.log_traceback(False)

        self._available = True

    def start(self):
        super(OculusDK2, self).start()

        for device in self._devices:
            device.start()

    def run(self):
        super(OculusDK2, self).run()

        for device in self._devices:
            device.run()

    def checkMethods(self):
        if not self._available:
            self.logger.info('Oculus DK2 python module not available !')
            return False

        if not self._devices:
            self.logger.info('Oculus DK2 python module not available ! No valid user found.')
            return False

        for device in self._devices:
            if not device.checkMethod(True):
                self.logger.info('No Oculus DK2 processor method available for user {0}!'.format(device.getName()))
                del device

        return True
