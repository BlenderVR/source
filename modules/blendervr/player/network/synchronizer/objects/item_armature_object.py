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

from . import item_object
from ....buffer import Buffer

class ArmatureObject:

    OBJECT =   b'o'
    FRAME  =   b'f'

    def _getSubItems(self):
        return list(self._item.channels)

class Master(ArmatureObject, item_object.Master):
    def __init__(self, parent, item):
        ArmatureObject.__init__(self)
        item_object.Master.__init__(self, parent, item)
        self._curentActionFrame = None

    def getSynchronizerBuffer(self):
        buffer = Buffer()

        object_buffer = item_object.Master.getSynchronizerBuffer(self)
        if len(object_buffer) > 0:
            buffer.command(self.OBJECT)
            buffer.subBuffer(object_buffer)

        if (self._curentActionFrame != self._item.getActionFrame()):
            self._curentActionFrame = self._item.getActionFrame()
            buffer.command(self.FRAME)
            buffer.float(self._curentActionFrame)
        return buffer

class Slave(ArmatureObject, item_object.Slave):
    def __init__(self, parent, item):
        ArmatureObject.__init__(self)
        item_object.Slave.__init__(self, parent, item)

    def processSynchronizerBuffer(self, buffer):

        while len(buffer) > 0:
            command = buffer.command()

            if command == self.OBJECT:
                object_buffer = buffer.subBuffer()
                item_object.Slave.processSynchronizerBuffer(self, object_buffer)

            if command == self.FRAME:
                actionFrame = buffer.float()
                self._item.setActionFrame(actionFrame)
                self._item.update()
