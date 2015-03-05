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
from ..protocol import decomposeMessage
from ..protocol import composeMessage
import sys

class UI(base.Client):
    def __init__(self, parent, client):
        base.Client.__init__(self, parent, client)
        self._mappings = {'configuration': ['config', 'file'],
                          'simulation file': ['simulation', 'blender', 'file'],
                          'processor file': ['simulation', 'processor', 'file'],
                          'screen set':['virtual environment', 'screen set']}
        self._debugs = {'processor':   ['debug', 'processor'],
                        'daemon':      ['debug', 'daemon'],
                        'executables': ['debug', 'executables'],
                        'updater':     ['debug', 'updater']}

    def cb_data(self):
        result = self._client.receive()
        command, argument = result
        if command == 'kill':
            sys.exit()
        if command == 'ping':
            self.logger.debug('Ping !')
            self._client.send(command, argument)
            return
        if command == 'set':
            self.set(argument)
            return
        if command == 'get':
            self.get(argument)
            return
        if command == 'start' or command == 'stop':
            self.controller.runAction(command, argument)
            return
        if command == 'status':
            self.status(argument)
            return
        if command == 'reload configuration':
            self.controller.configuration()
            return
        if command == 'update loader':
            self.controller.updateLoader()
            return
        if command == 'debug':
            self.debug(argument)
            return
        self.logger.debug('unknown command:', command, '(', argument, ')')

    def set(self, argument):
        command, argument = decomposeMessage(argument)
        if command in self._mappings:
            self.profile.setValue(self._mappings[command], argument)
            if command == 'configuration':
                self.controller.configuration()
            if command == 'screen set':
                self.controller.screenSet()
            return

    def get(self, command):
        if command in self._mappings:
            self._client.send('get', composeMessage(command, self.profile.getValue(self._mappings[command])))
            return
        if command == 'screen sets':
            self._client.send('get', composeMessage(command, self.controller.getScreenSets()))
            return
        
    def debug(self, argument):
        command, argument = decomposeMessage(argument)
        if command in self._debugs:
            self.profile.setValue(self._debugs[command], argument)

    def status(self, command):
        if command == 'simulation':
            self._client.send('status', composeMessage(command, False))
            return

    def status(self, command):
        if command == 'simulation':
            self._client.send('status', composeMessage(command, False))
            return
