# -*- coding: utf-8 -*-
# file: blendervr/plugins/osc/xml.py

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

import os
from .. import xml


class XML(xml.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._attribute_list += ['host', 'port', 'configuration']
        self._class_list += ['users']
        #self._class_list     += ['room']
        if 'host' in attrs:
            self._host = attrs['host']
        else:
            self._host = None
        if 'port' in attrs:
            self._port = attrs['port']
        else:
            self._port = None
        if 'configuration' in attrs:
            self._configuration = attrs['configuration']
        else:
            self._configuration = None

        self._users = None

    def _getChildren(self, name, attrs):
        if name == 'room':
            self._room = Room(self, name, attrs)
            return self._room
        if name == 'user':
            user = User(self, name, attrs)
            if self._users is None:
                self._users = [user]
            else:
                self._users.append(user)
            return user


class Room(xml.mono):
    def __init__(self, parent, name, attrs):
        super(Room, self).__init__(parent, name, attrs)
        self._attribute_list += ['warmth', 'brightness', 'presence',
                                 'reverb_volume', 'running_reverb',
                                 'late_reverb', 'envelop', 'heavyness',
                                 'livelyness']
        for attribute in self._attribute_list:
            if hasattr(self, '_' + attribute):
                setattr(self, '_' + attribute, attrs[attribute])
            else:
                setattr(self, '_' + attribute, None)


class User(xml.mono):
    def __init__(self, parent, name, attrs):
        super(User, self).__init__(parent, name, attrs)
        self._attribute_list += ['listener', 'viewer']

        if 'listener' not in attrs:
            self.raise_error('OSC User must at least have a listener !')
        self._listener = attrs['listener']

        if 'viewer' in attrs:
            self._viewer = attrs['viewer']
        else:
            self._viewer = None
