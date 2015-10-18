# -*- coding: utf-8 -*-
# file: blendervr/plugins/vrpn/virtual_environment/__init__.py

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
from ....player import exceptions


class VRPN(base.Base):
    def __init__(self, parent, configuration):
        super(VRPN, self).__init__(parent)

        self._devices = []
        self._display_processors = configuration['display_processors']

        try:
            import vrpn
            assert vrpn     # avoid import unused
            from . import tracker
            from . import analog
            from . import button
            from . import text
        except ImportError as e:
            self.logger.info('No VRPN python module available, reason:',e)
            self._available = False
            return

        try:
            device_types = {'button': button.Button,
                            'analog': analog.Analog,
                            'tracker': tracker.Tracker,
                            'text': text.Text}
        except NameError:
            pass
        else:
            for key, className in device_types.items():
                if (key in configuration) and configuration[key] is not None:
                    for element in configuration[key]:
                        try:
                            self._devices.append(className(self, element))
                        except exceptions.Processor_Invalid_Device_Method \
                                                                as method:
                            if self._display_processors:
                                self.logger.warning(method)
                        except exceptions.Processor_Invalid_Device as other:
                            self.logger.warning(other)
        self._available = True

    def checkMethods(self):
        if not self._available:
            self.logger.info('VRPN python module not available !')
            return False
        invalid = []
        for device in self._devices:
            if not device.checkMethod(self._display_processors):
                invalid.append(device)
        for device in invalid:
            self._devices.remove(device)
        if len(self._devices) == 0:
            self.logger.info('No VRPN processor method available !')
            return False
        return True

    def start(self):
        for device in self._devices:
            device.start()

    def run(self):
        for device in self._devices:
            device.run()
