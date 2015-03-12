# -*- coding: utf-8 -*-
# file: blendervr/plugins/osc/virtual_environment/__init__.py

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

import socket
from ....player import user as bc_user
from .. import base as bc_base, client, exceptions
from . import base, object, user, objectuser

class OSC(bc_base.Base):
    def __init__(self, parent,  configuration):
        super(OSC, self).__init__(parent)

        self.stateToggle = None

        self._global = base.Base(self, 'global', None)

        self._global._commands['configuration'] = { 'type'  : 'string' }
        self._global._commands['reset']         = { 'type'  : 'none' }

        if 'configuration' in configuration:
            self._global._commands['configuration']['value'] = configuration['configuration']

        self._global._commands_order = ['reset', 'configuration', 'volume', 'start', 'mute']

        self._global.define_commands()

        self.logger.debug('room acoustic through OSC is not implemented for the moment !')
        if 'room' in configuration and False:
            for attribut in global_attributs:
                if attribut in configuration['room']:
                    getattr(self._global, attribut)(configuration['room'][attribut])

        self._objects    = {}

        self._viewers   = {}
        self._users      = {}
        self._userObject = {}
        if 'users' in configuration:
            for index, user_entry in enumerate(configuration['users']):
                try:
                    listener = user.User(self, user_entry, index)
                    self._users[listener.getName()] = listener
                    viewer = listener.getUser()
                    if viewer is not None:
                        self._viewers[id(viewer)] = listener
                    self._userObject[listener.getID_1()] = {}
                except:
                    self.logger.log_traceback(False)

        if configuration['host'] and configuration['port']:
            try: # whatever error inside OSC, we don't create the client !
                self._client = client.Client(self, configuration['host'], configuration['port'])
            except:
                pass
        self._first_try = True

    def __del__(self):
        self._close()

    def _close(self):
        del(self._client)

    def isAvailable(self):
        """
        Return true if the OSC client is available, else return false
        """
        return hasattr(self, '_client')

    def reset(self):
        """
        Send '/global/reset' message to the OSC client
        """
        if hasattr(self, '_client'):
            cmd = msg.MSG(self, '/global')
            cmd.append('reset')
            self.sendCommand(cmd)

    def getObject(self, obj):
        """
        Instantiate/Access OSC_Object attached to a KX_GameObject, return OSC_Object

        :param obj: KX_GameObject in the scene
        :type obj: KX_GameObject
        """
        id_obj = id(obj)
        if id_obj in self._objects:
            return self._objects[id_obj]
        self._objects[id_obj] = object.Object(self, obj)
        return self._objects[id_obj]

    def getUser(self, usr):
        """
        Instantiate OSC_User attached to a viewer, return OSC_User

        :param usr: listener, defined in the .xml configuration file
        :type usr: string
        """
        if isinstance(usr, str):
            if usr in self._users:
                return self._users[usr]
        if isinstance(usr, bc_user.User):
            id_usr = id(usr)
            if id_usr in self._viewers:
                return self._viewers[id_usr]
        return None

    def getObjectUser(self, obj, usr):
        """
        Instantiate OSC_ObjectUser, the 'audio link' between OSC_User and OSC_Object

        :param obj: OSC_Object
        :type obj: OSC_Object
        :param obj: OSC_User
        :type obj: OSC_User
        """
        if (not isinstance(obj, object.Object)) or (not isinstance(usr, user.User)):
            raise exceptions.OSC_Invalid_Type('getObjectUser waits a user then an object')
        id_usr = usr.getID_1()
        if id_usr in self._userObject:
            usr_obj = self._userObject[usr.getID_1()]
            id_obj  = obj.getID_1()
            if id_obj in usr_obj:
                return usr_obj[id_obj]
            usr_obj[id_obj] = objectuser.ObjectUser(self, obj, usr)
            return usr_obj[id_obj]
        return None

    def start(self):
        pass

    def reset(self):
        self._global.reset();
        self._global.runAttribut(self._global.getAttribut('reset'))

    def run(self):
        if hasattr(self, '_client'):
            try:
                self._global.run()
                for id, object in self._objects.items():
                    object.run()
                for id, listener in self._users.items():
                    listener.run()
                for id, objects in self._userObject.items():
                    for id, object in objects.items():
                        object.run()
            except socket.error:
                if self._first_try:
                    self.logger.warning('Cannot send command to OSC host => stop OSC !')
                else:
                    self.logger.log_traceback(False)
                self._close()
                raise exceptions.PluginError()
            self._first_try = False

    def sendCommand(self, cmd):
        if hasattr(self, '_client'):
            self._client.send(cmd)

    def getGlobal(self):
        """
        Return handle on OSC_global, a controller for high level sound control, defined in ./base.py

        getGlobal().start(True):
        send OSC message '/global/start 1'

        getGlobal().volume(30) / getGlobal().volume(-3):
        send OSC message '/global/volume 30' and '/global/volume -3'

        getGlobal().mute(False):
        send OSC message '/global/mute 0'
        """
        return self._global
