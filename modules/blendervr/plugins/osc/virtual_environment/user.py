# -*- coding: utf-8 -*-
# file: blendervr/plugins/osc/virtual_environment/user.py

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

from . import base
#import bge
#import mathutils
#import math


class User(base.Base):
    def __init__(self, parent, configuration, id):
        super(User, self).__init__(parent, 'user', id)

        if configuration['viewer'] is not None:
            self._viewer = self.blenderVR.getUserByName(configuration['viewer'])
        else:
            self._viewer = None
        self._listener_name = configuration['listener']
        self._commands['name'] = {'type': 'string'}
        self._commands['position'] = {'type': 'matrix'}
        self._commands['hrtf'] = {'type': 'int'}
        attributs = ['warmth', 'brightness', 'presence',
                     'reverb_volume', 'running_reverb',
                     'late_reverb', 'envelop', 'heavyness',
                     'livelyness']
        for attribut in attributs:
            self._commands[attribut] = {'type': 'int'}

        self._commands_order = ['name', 'hrtf', 'volume', 'position',
                                'start', 'mute'] + attributs
        self.define_commands()
        self.name(self._listener_name)
        if self._viewer is not None:
            self._viewer.blenderVR_OSC = self

    def run(self):
        if self._viewer is not None:
            self.position(self._viewer.getPosition()
                          * self._viewer.getVehiclePosition())
        super(User, self).run()

    def getName(self):
        return self._listener_name

    def getUser(self):
        return self._viewer
