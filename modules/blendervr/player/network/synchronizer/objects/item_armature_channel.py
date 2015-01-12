# -*- coding: utf-8 -*-
# file: blendervr/player/network/synchronizer/objects/item_armature_channel.py

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

from . import item_base
from ....buffer import Buffer


class ArmatureChannel:
    pass


class Master(ArmatureChannel, item_base.Master):
    def __init__(self, parent, item):
        ArmatureChannel.__init__(self)
        item_base.Master.__init__(self, parent, item)

    def getSynchronizerBuffer(self):
        buff = Buffer()
        buff.vector_3(self._item.location)
        buff.vector_3(self._item.scale)
        # Don't use joint_rotation as its computation is link to robotic
        # application, thus, slaves don't care as it should be done on
        # the master
        rotation_mode = self._item.rotation_mode
        buff.integer(rotation_mode)
        if rotation_mode == 0:
            buff.vector_4(self._item.rotation_quaternion)
        else:
            buff.vector_3(self._item.rotation_euler)
        return buff


class Slave(ArmatureChannel, item_base.Slave):
    def __init__(self, parent, item):
        ArmatureChannel.__init__(self)
        item_base.Slave.__init__(self, parent, item)

    def processSynchronizerBuffer(self, buff):
        self._item.location = buff.vector_3()
        self._item.scale = buff.vector_3()
        rotation_mode = buff.integer()
        self._item.rotation_mode = rotation_mode
        if rotation_mode == 0:
            self._item.rotation_quaternion = buff.vector_4()
        else:
            self._item.rotation_euler = buff.vector_3()
        self._parent_synchronizer._item.update()
