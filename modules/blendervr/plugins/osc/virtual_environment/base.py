# -*- coding: utf-8 -*-
# file: blendervr/plugins/osc/virtual_environment/base.py

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

from ... import base
from .. import exceptions
from .. import msg
import mathutils


class Base(base.Base):
    def __init__(self, parent, name, OSC_ID_1=None, OSC_ID_2=None):
        super(Base, self).__init__(parent)
        self._name = name
        self._OSC_ID_1 = OSC_ID_1
        self._OSC_ID_2 = OSC_ID_2
        self._commands = {
            'start': {'type': 'state'},
            'volume': {'type': 'vol'},
            'mute': {'type': 'state'}
            }
        self._commands_order = ['volume', 'start', 'mute']

    def runAttribut(self, attribut):
        if attribut['update']:
            cmd = msg.MSG(self, '/' + self._name)
            if self._OSC_ID_1 is not None:
                cmd.append(self._OSC_ID_1)
            if self._OSC_ID_2 is not None:
                cmd.append(self._OSC_ID_2)
            cmd.append(attribut['cmd'])
            if attribut['value'] is not None:
                cmd.append(attribut['value'])
            self.getParent().sendCommand(cmd)
            attribut['update'] = False

    def run(self):
        for name in self._commands_order:
            self.runAttribut(self._commands[name])

    def getID_1(self):
        return self._OSC_ID_1

    def getID_2(self):
        return self._OSC_ID_2

    def getAttribut(self, name):
        return self._commands[name]

    def _command_none(self, attribut):
        attribut['update'] = True

    def _command_bool(self, attribut, value):
        if isinstance(value, bool):
            if value is True:
                value = 1
            else:
                value = 0
            if attribut['value'] != value:
                attribut['value'] = value
                attribut['update'] = True
            return
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not a boolean')

    def _command_state(self, attribut, value=None, force=False):
        if value is None:
            attribut['value'] = -1
            attribut['update'] = True
            return
        if isinstance(value, bool):
            if value is True:
                value = 1
            else:
                value = 0
            if force or (attribut['value'] != value):
                attribut['value'] = value
                attribut['update'] = True
            return
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not a valid state')

    def _command_int(self, attribut, value):
        if isinstance(value, int):
            if attribut['value'] != value:
                attribut['value'] = value
                attribut['update'] = True
            return
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not an integer')

    def _command_matrix(self, attribut, value):
        if isinstance(value, mathutils.Matrix):
            value = [value[0][0], value[1][0], value[2][0], value[3][0],
                     value[0][1], value[1][1], value[2][1], value[3][1],
                     value[0][2], value[1][2], value[2][2], value[3][2],
                     value[0][3], value[1][3], value[2][3], value[3][3]]
            if attribut['value'] != value:
                attribut['value'] = value
                attribut['update'] = True
            return
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not a matrix')

    def _command_string(self, attribut, value):
        if isinstance(value, str):
            if attribut['value'] != value:
                attribut['value'] = value
                attribut['update'] = True
            return
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not a string')

    def _command_vol(self, attribut, value):
        if isinstance(value, str):
            if value[0] == '%' or value[0] == '+' or value[0] == '-':
                try:
                    value = value[0] + str(int(value[1:]))
                    if attribut['value'] != value \
                                    or value[0] == '+' or value[0] == '-':
                        attribut['value'] = value
                        attribut['update'] = True
                    return
                except:
                    pass
        raise exceptions.OSC_Invalid_Type(str(value) + ' is not a valid '
                                            'volume (%32, +5, -17)')

    def define_commands(self):
        from types import MethodType
        for name, attribut in self._commands.items():
            if 'cmd' not in attribut:
                attribut['cmd'] = name
            setattr(self, name, MethodType(getattr(self, '_command_'
                                            + attribut['type']), attribut))
            attribut['update'] = True
            if 'value' not in attribut:
                if attribut['type'] == 'none':
                    attribut['value'] = None
                    attribut['update'] = False
                elif attribut['type'] == 'int':
                    attribut['value'] = 0
                elif attribut['type'] == 'vol':
                    attribut['value'] = '%50'
                elif (attribut['type'] == 'bool') \
                                    or (attribut['type'] == 'state'):
                    attribut['value'] = 0
                else:
                    attribut['value'] = ''
