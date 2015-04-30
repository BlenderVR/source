# -*- coding: utf-8 -*-
# file: blendervr/player/user.py

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

import mathutils
from .base import Base
from .buffer import Buffer
import bge


class User(Base):

    SYNCHRONIZER_COMMAND_USER_POSITION = b'u'
    SYNCHRONIZER_COMMAND_VEHICLE_POSITION = b'v'

    def __init__(self, parent, id, config):
        super(User, self).__init__(parent)

        self._id = id
        self._name = config['name']
        self._eye_separation = config['behavior']['eye_separation']
        self._default_position = mathutils.Matrix.Translation(
                            (config['behavior']['default_position']))
        self._default_rotation = mathutils.Euler(
                            (config['behavior']['default_rotation']))

        self._position = self._default_position * self._default_rotation.to_matrix().to_4x4()
        self._vehicle_position = mathutils.Matrix()

        self._previous = {'user_position': 0,
                          'vehicle_position': 0}

        self._parent = None

        self.BlenderVR.addObjectToSynchronize(self,
                                    'userSynchronization-' + self._name)

    def getID(self):
        return self._id

    def getName(self):
        return self._name

    def getPosition(self):
        """
        get user position in the virtual environment.

        Args: None

        Returns: 4x4 mathutils.Matrix (rotation and location).
        """
        return self._position

    def getVehiclePosition(self, internal=False):
        if isinstance(self._parent, User) and not internal:
            return self._vehicle_position * self._parent.getVehiclePosition()
        if isinstance(self._parent, bge.types.KX_GameObject) and not internal:
            return (self._vehicle_position *
                    self._parent.worldTransform.inverted() *
                    bge.logic.getCurrentScene().active_camera.worldTransform)
        return self._vehicle_position

    def getEyeSeparation(self):
        return self._eye_separation

    def setPosition(self, position):
        self._position = position

    def setVehiclePosition(self, position):
        self._vehicle_position = position

    def resetVehiclePosition(self):
        self._vehicle_position = mathutils.Matrix()

    def setParent(self, parent):
        if parent is not self:  # Avoid loop ...
            self._parent = parent

    # Both methods are use for the synchronization mechanism ...
    def getSynchronizerBuffer(self):
        buff = Buffer()

        if (self._previous['user_position'] != self.getPosition()):
            self._previous['user_position'] = self.getPosition()
            buff.command(self.SYNCHRONIZER_COMMAND_USER_POSITION)
            buff.matrix_4x4(self.getPosition())

        if (self._previous['vehicle_position'] != self.getVehiclePosition()):
            self._previous['vehicle_position'] = self.getVehiclePosition()
            buff.command(self.SYNCHRONIZER_COMMAND_VEHICLE_POSITION)
            buff.matrix_4x4(self.getVehiclePosition())

        return buff

    def processSynchronizerBuffer(self, buff):
        while not buff.isEmpty():
            command = buff.command()

            if (command == self.SYNCHRONIZER_COMMAND_USER_POSITION):
                self.setPosition(buff.matrix_4x4())

            elif (command == self.SYNCHRONIZER_COMMAND_VEHICLE_POSITION):
                self.setVehiclePosition(buff.matrix_4x4())

    @property
    def localTransform(self):
        return self._vehicle_position

    @property
    def worldTransform(self):
        try:
            return (self._vehicle_position *
                    self._parent.worldTransform.inverted() *
                    bge.logic.getCurrentScene().active_camera.worldTransform)
        except:
            return self._vehicle_position
