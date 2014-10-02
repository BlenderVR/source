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

    POSITION    =   b'p'
    ORIENTATION =   b'o'
    SCALE       =   b's'
    VISIBILITY  =   b'v'
 
    def default(self):
        pass

class Master(Object, item_base.Master):
    def __init__(self, parent, item):
        Object.__init__(self)
        item_base.Master.__init__(self, parent, item)
        self._previousPosition    = mathutils.Vector()
        self._previousOrientation = mathutils.Matrix()
        self._previousScale       = mathutils.Vector()
        self._previousVisibility  = True

    def getSynchronizerBuffer(self):
        buffer = Buffer()

        if self._previousPosition != self._item.worldPosition:
            self._previousPosition = copy.copy(self._item.worldPosition)
            buffer.command(self.POSITION)
            buffer.vector_3(self._previousPosition)
            
        if self._previousOrientation != self._item.worldOrientation:
            self._previousOrientation = copy.copy(self._item.worldOrientation)
            buffer.command(self.ORIENTATION)
            buffer.matrix_3x3(self._previousOrientation)
            
        if self._previousScale != self._item.worldScale:
            self._previousScale = copy.copy(self._item.worldScale)
            buffer.command(self.SCALE)
            buffer.vector_3(self._previousScale)

        if self._previousVisibility != self._item.visible:
            self._previousVisibility = self._item.visible
            buffer.command(self.VISIBILITY)
            buffer.boolean(self._previousVisibility)

        return buffer

class Slave(Object, item_base.Slave):
    def __init__(self, parent, item):
        Object.__init__(self)
        item_base.Slave.__init__(self, parent, item)

    def processSynchronizerBuffer(self, buffer):

        while len(buffer) > 0:
            command = buffer.command()

            if command == self.POSITION:
                self._item.worldPosition = buffer.vector_3()
            
            if command == self.ORIENTATION:
                self._item.worldOrientation = buffer.matrix_3x3()
            
            if command == self.SCALE:
                self._item.worldScale = buffer.vector_3()

            if command == self.VISIBILITY:
                self._item.setVisible(buffer.boolean())
