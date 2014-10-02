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

class Scene:
    def default(self):
        return

    def _getSubItems(self):
        return list(self._item.objects)

class Master(Scene, item_base.Master):
    def __init__(self, parent, item):
        Scene.__init__(self)
        item_base.Master.__init__(self, parent, item)
        self._previousCamera = self._item.active_camera
        self._created        = False

    def getSynchronizerBuffer(self):
        buffer = Buffer()
        if self._previousCamera != self._item.active_camera:
            self._previousCamera = self._item.active_camera
            buffer.string(str(self._previousCamera))
        return buffer

class Slave(Scene, item_base.Slave):
    def __init__(self, parent, buffer):
        Scene.__init__(self)
        item_base.Slave.__init__(self, parent, buffer)

    def getItemByName(self, name, sg_parent):
        item = item_base.Slave.getItemByName(self, name, sg_parent)
        if item is None:
            if sg_parent != 0:
                parent = self.getParent().getObjectByMasterID(sg_parent)
                if parent:
                    parent = parent._item
                else:
                    parent = name
            else:
                parent = name
            item = self._item.addObject(name, parent)
        return item

    def processSynchronizerBuffer(self, buffer):
        camera_name = buffer.string()
        try:
            self._item.active_camera = self._item.objects[camera_name]
        except:
            pass
