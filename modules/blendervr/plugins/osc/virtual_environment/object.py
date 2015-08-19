# -*- coding: utf-8 -*-
# file: blendervr/plugins/osc/virtual_environment/object.py

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

from . import base
import bge
from .. import exceptions


class Object(base.Base):
    def __init__(self, parent, obj):
        super(Object, self).__init__(parent, 'object', len(parent._objects) + 1)
        if isinstance(obj, str):
            self._object = bge.logic.getCurrentScene().objects[obj]
        elif isinstance(obj, bge.types.KX_GameObject):
            self._object = obj
        else:
            raise exceptions.OSC_Invalid_Object(str(obj))
        if id(self._object) in self.getParent()._objects:
            raise exceptions.OSC_Invalid_Already_Created(str(obj))
        self._commands['sound'] = {'type': 'string'}
        self._commands['position'] = {'type': 'matrix'}
        self._commands['loop'] = {'type': 'state'}
        self._commands['release'] = {'type': 'state'}
        self._commands_order = ['release', 'sound', 'loop', 'volume',
                                'start', 'position', 'mute']
        self.define_commands()

    def run(self):
        camera = bge.logic.getCurrentScene().active_camera
        camera_position = camera.worldOrientation.to_4x4()
        camera_position[0][3] = camera.worldPosition[0]
        camera_position[1][3] = camera.worldPosition[1]
        camera_position[2][3] = camera.worldPosition[2]
        object_position = self._object.worldOrientation.to_4x4()
        object_position[0][3] = self._object.worldPosition[0]
        object_position[1][3] = self._object.worldPosition[1]
        object_position[2][3] = self._object.worldPosition[2]
        self.position(camera_position.inverted() * object_position)

        self.checkIfObjectHasBeenReleased()
        super(Object, self).run()

    def getName(self):
        return self._object.name

    def getObject(self):
        return self._object

    def checkIfObjectHasBeenReleased(self):
        """
        Check if OSC object has been released. Delete OSC object and
        its associated userObject links from stored dictionaries.
        Mecanism to limit (reuse) the number of objects instantiated
        in the OSC client (e.g. sound objects in Max/MSP).

        Args: None

        Returns: Bool, True if object has been released
        """

        attribut = self._commands['release']
        if attribut['update'] and attribut['value']==1:

            try: ## del osc object_user from _userObject dict
                for key, item in self._parent._users.items(): # for all osc users
                    id_usr = item.getID_1()
                    if id_usr in self._parent._userObject: # if a userObject link exists for this osc user
                        usr_obj = self._parent._userObject[id_usr] # get osc user
                        id_obj  = self._OSC_ID_1 # get osc object
                        if id_obj in usr_obj.keys(): # if an objectUser link exists between osc object and osc user
                            del(usr_obj[id_obj]) # delete said link

            except:
                self.logger.log_traceback(False)

            ## del osc object from _objects dict
            del(self.getParent()._objects[id(self._object)])
