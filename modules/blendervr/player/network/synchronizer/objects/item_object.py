# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/item_object.py

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

import copy
import mathutils
from . import item_base
from ....buffer import Buffer


class Object:

    POSITION = b'p'
    ORIENTATION = b'o'
    SCALE = b's'
    VISIBILITY = b'v'
    COLOR3 = b'd'
    COLOR4 = b'c'

    def default(self):
        pass


class Master(Object, item_base.Master):
    def __init__(self, parent, item):
        Object.__init__(self)
        item_base.Master.__init__(self, parent, item)
        self._previousPosition = mathutils.Vector()
        self._previousOrientation = mathutils.Matrix()
        self._previousScale = mathutils.Vector()
        self._previousVisibility = True
        self._previousColor = mathutils.Vector((0.8,0.8,0.8,1.0))


    def getSynchronizerBuffer(self):
        buff = Buffer()

        if self._previousPosition != self._item.worldPosition:
            self._previousPosition = copy.copy(self._item.worldPosition)
            buff.command(self.POSITION)
            buff.vector_3(self._previousPosition)

        if self._previousOrientation != self._item.worldOrientation:
            self._previousOrientation = copy.copy(self._item.worldOrientation)
            buff.command(self.ORIENTATION)
            buff.matrix_3x3(self._previousOrientation)

        if self._previousScale != self._item.worldScale:
            self._previousScale = copy.copy(self._item.worldScale)
            buff.command(self.SCALE)
            buff.vector_3(self._previousScale)

        if self._previousVisibility != self._item.visible:
            self._previousVisibility = self._item.visible
            buff.command(self.VISIBILITY)
            buff.boolean(self._previousVisibility)

        if self._previousColor != self._item.color:
            self._previousColor = self._item.color.copy()
            if len(self._item.color) == 4:
                buff.command(self.COLOR4)
                buff.vector_4(self._previousColor)
            if len(self._item.color) == 3:
                buff.command(self.COLOR3)
                buff.vector_3(self._previousColor)

        return buff


class Slave(Object, item_base.Slave):
    def __init__(self, parent, item):
        Object.__init__(self)
        item_base.Slave.__init__(self, parent, item)


    def _processCommand(self, command, buff):
        if command == self.POSITION:
            self._item.worldPosition = buff.vector_3()

        if command == self.ORIENTATION:
            self._item.worldOrientation = buff.matrix_3x3()

        if command == self.SCALE:
            self._item.worldScale = buff.vector_3()

        if command == self.VISIBILITY:
            self._item.setVisible(buff.boolean())

        if command == self.COLOR3:
            self._item.color = buff.vector_3()

        if command == self.COLOR4:
            self._item.color = buff.vector_4()

    def processSynchronizerBuffer(self, buff):
        while len(buff) > 0:
            command = buff.command()
            self._processCommand(command, buff)

