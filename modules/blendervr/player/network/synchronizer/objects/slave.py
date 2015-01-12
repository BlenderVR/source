# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/slave.py

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

#import copy
#import bge
from .... import exceptions
from . import Synchronizer


class Slave(Synchronizer):
    def __init__(self, parent):
        Synchronizer.__init__(self, parent)

    def start(self):
        Synchronizer.start(self)
        self._synchronizer.addSynchronizedObject(0, self._root)

    def processSynchronizerBuffer(self, buff):

        while len(buff) > 0:
            command = buff.command()

            if command == self.DELETE_ITEM:
                master_item_id = buff.itemID()
                sync_item = self._synchronizer.removeSynchronizedObject(
                                                            master_item_id)
                if sync_item:
                    local_item_id = sync_item.getItemID()
                    if local_item_id in self._items:
                        del(self._items[local_item_id])
                    if hasattr(sync_item, '_parent_synchronizer'):
                        sync_item._parent_synchronizer.removeChildren(sync_item)
                    del(sync_item)
                continue

            if command == self.CREATE_ITEM:
                children_id = buff.itemID()
                children_name = buff.string()
                parent_id = buff.itemID()
                sg_parent = buff.itemID()
                parent_item = self.getObjectByMasterID(parent_id)
                if not parent_item:
                    continue
                children = parent_item.getItemByName(children_name, sg_parent)
                self._synchronizer.addSynchronizedObject(children_id,
                                                    self.getItem(children))
                continue

            raise exceptions.Synchronizer("buffer from master reading error:"
                                          " not start of item ("
                                          + str(command) + ") !")
        return

    def getObjectByMasterID(self, master_id):
        return self._synchronizer.getObjectByID(master_id)
