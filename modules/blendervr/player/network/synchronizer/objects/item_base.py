# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/item_base.py

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

from .... import base
from ....buffer import Buffer
import bge
import copy


class NotExistingItem(Exception):
    pass


class Base(base.Base):
    def __init__(self, parent, item):
        base.Base.__init__(self, parent)
        self._item = item
        self._itemID = id(item)
        self._name = str(self._item)
        self.default()

        self._items_bl = []
        self._items_sy = []

    def __del__(self):
        try:
            self._item.endObject()
            if not self.BlenderVR.isMaster():
                bge.logic.getCurrentScene().resume()
        except:
            pass
        del(self._item)
        self._item = None

    def checkItems(self):
        if hasattr(self._item, 'invalid') and self._item.invalid:
            self.remove()
            existing = False
        else:
            str(self._item)
            for item in list(set(self._getSubItems()) - set(self._items_bl)):
                self.addChildren(item)
            existing = True

        remove_items = []
        for item in self._items_sy:
            try:
                item.checkItems()
            except NotExistingItem:
                remove_items.append(item)

        for item in remove_items:
            self._items_sy.remove(item)

        if not existing:
            raise NotExistingItem()

    def addChildren(self, children):
        self._items_bl.append(children)
        children = self.getParent().getItem(children)
        children._parent_synchronizer = self
        self._items_sy.append(children)
        return children

    def remove(self):
        self.getParent().removeSynchronizedItem(self._itemID)

    def getItemID(self):
        return self._itemID

    def __str__(self):
        return self._name

    def default(self):
        pass

    def isSynchronizable(self):
        return True

    def _getSubItems(self):
        return []


class Master(Base):
    def __init__(self, parent, item):
        Base.__init__(self, parent, item)
        self._created = False

    def __del__(self):
        Base.__del__(self)
        self.activate(False)

    def addChildren(self, children):
        children = Base.addChildren(self, children)
        self.getParent().addItem(children, self)

    def remove(self):
        self.getParent().removeItem(self)
        Base.remove(self)

    def getSynchronizerBuffer(self):
        return Buffer()

    def activate(self, enable, recursive=False):
        self.getParent()._activateItem(self, enable)
        if recursive:
            for item in self._getSubItems():
                item = self.getParent().getItem(item)
                item.activate(enable, True)


class Slave(Base):
    def __init__(self, parent, item):
        Base.__init__(self, parent, item)

    def getItemByName(self, name, sg_parent):
        for subItem in self._getSubItems():
            if str(subItem) == name:
                return subItem
        return None

    def processSynchronizerBuffer(self, buffer):
        return

    def removeChildren(self, children):
        # TODO: normally, we should not do the test ...
        if children._item in self._items_bl:
            self._items_bl.remove(children._item)
        if children in self._items_sy:
            self._items_sy.remove(children)

