# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/master.py

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

from ....buffer import Buffer
from . import Synchronizer


class Master(Synchronizer):
    def __init__(self, parent):
        self._items_update = Buffer()
        Synchronizer.__init__(self, parent)

    def _activateItem(self, synchronizerItem, activate):
        if synchronizerItem.isSynchronizable():
            item_id = synchronizerItem.getItemID()
            if activate:
                self._synchronizer.addSynchronizedObject(item_id,
                                                         synchronizerItem)
            else:
                self._synchronizer.removeSynchronizedObject(item_id)

    def getSynchronizerBuffer(self):
        return None

    def sendItemsUpdateToSlaves(self, buff):
        self._items_update += buff

    def addItem(self, children, parent):
        buff = Buffer()
        buff.command(self.CREATE_ITEM)
        buff.itemID(children.getItemID())
        buff.string(str(children))
        buff.itemID(parent.getItemID())
        if hasattr(children._item, 'parent') and \
                                    children._item.parent is not None:
            sg_parent = self.getItem(children._item.parent)
            buff.itemID(sg_parent.getItemID())
        else:
            buff.itemID(0)
        self.sendItemsUpdateToSlaves(buff)

    def removeItem(self, item):
        buff = Buffer()
        buff.command(self.DELETE_ITEM)
        buff.itemID(item.getItemID())
        self.sendItemsUpdateToSlaves(buff)

    def checkItems(self):
        Synchronizer.checkItems(self)
        buff = self._items_update
        self._items_update = Buffer()
        return buff
