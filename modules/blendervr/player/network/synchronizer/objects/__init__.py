# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/__init__.py

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

import bge
import importlib
from .... import base

class Synchronizer(base.Base):
    CREATE_ITEM = b'c'
    UPDATE_ITEM = b'u'
    END_UPDATE_ITEM = b'e'
    DELETE_ITEM = b'd'
    SET_ATTRIBUTE = b'a'

    def __init__(self, parent):
        base.Base.__init__(self, parent)
        self._synchronizer = parent

        self._item_types = {}
        item_types = {'module' : 'item_root',
                      'KX_Scene': 'item_scene',
                      'KX_GameObject': 'item_object',
                      'KX_LightObject': 'item_light',
                      'KX_Camera': 'item_camera',
                      'KX_FontObject': 'item_font',
                      'BL_ArmatureObject': 'item_armature_object',
                      'BL_ArmatureChannel': 'item_armature_channel',
                      #'BL_ArmatureBone'    : 'item_armature_bone',
                      # !Bones are fully read-only. So we can't update it !
                      'default': 'item_default'}

        for item_name, module_name in item_types.items():
            try:
                self._item_types[item_name] = importlib.import_module(
                                            __name__ + '.' + module_name)
            except ImportError:
                self.logger.debug('unimplemented blender item type : ' +
                                                                item_name)

        self._synchronizer.addObjectToSynchronize(self,
                                    'Blender objects synchronization system')
        self._alreadyStart = False

        self._items = {}

    def start(self):
        self._root = self.getItem(bge.logic)
        self._root.checkItems()

    def getItem(self, item):
        item_id = id(item)
        if item_id not in self._items:
            synchronizerItem = item_type = item.__class__.__name__
            assert synchronizerItem    # avoid initialized but unused
            try:
                module = self._item_types[item_type]
            except KeyError:
                self.logger.warning('unrocognized type : ' + item_type)
                module = self._item_types['default']
            if self.blenderVR.isMaster():
                self._items[item_id] = module.Master(self, item)
            else:
                self._items[item_id] = module.Slave(self, item)
        return self._items[item_id]

    def removeSynchronizedItem(self, itemID):
        if itemID in self._items:
            del(self._items[itemID])
        self._synchronizer.removeSynchronizedObject(itemID)

    def checkItems(self):
        self._root.checkItems()
