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
import sys
import os
from .. import base
from ...tools import connector
import select

class Controller(base.Base):

    def __init__(self, parent):
        super(Controller, self).__init__(parent)

        controller  = sys.argv[(sys.argv.index('-')+1)]
        # in case of space inside the name of the screen, the quotes and the double-quotes remains in the argument
        screen_name = sys.argv[(sys.argv.index('-')+2)].strip("'\"")

        self._client = connector.Client(controller, 'blender_player', screen_name)
        self._client.setCallback(self._waitForConfiguration)
        self._client.setWait(True)
        
        self.logger.addLoginWindow(self)

        self._log_to_controller = False
        self._processor_command = False
        self._file_logging      = None

        self._configuration = {'screen_name': screen_name}

        if not self._client.run():
            self.blenderVR.quit('Loosed the console')

    def _waitForConfiguration(self, command, argument):
        if command == 'base configuration ending':
            self._client.setCallback(self._processControllerCommand)
            self._client.setWait(False)
            return

        if command in ['screen', 'complements', 'network', 'blender_file', 'processor_files']:
            self._configuration[command] = argument
        else:
            self._processControllerCommand(command, argument)

    def write(self, *messages):
        if not self._log_to_controller:
            return
        elements = []
        for message in messages:
            elements.append(str(message))
        for message in (' '.join(elements)).split('\n'):
            self._sendToConsole('log', message.rstrip(' \n\r'))

    def flush(self):
        pass

    def _processControllerCommand(self, command, argument):
        if command == 'log_level':
            self.logger.setLevel(argument)
        elif command == 'log_to_controller':
            self._log_to_controller = argument
        elif command == 'quit':
            self.blenderVR.quit('Asked by the user through the console')
        elif command == 'console_to_virtual_environment':
            if self.blenderVR.getProcessor() is not None and self.blenderVR.isMaster():
                command, argument = connector.Common.decomposeMessage(argument)
                self.blenderVR.getProcessor().receivedFromConsole(command, argument)
        elif command == 'log_file':
            if argument:
                if not self._file_logging:
                    path_name = os.path.dirname(argument)
                    if not os.path.isdir(path_name):
                        os.makedirs(path_name)

                    import logging
                    self._file_logging = logging.FileHandler(argument)
                    self._file_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
                    self.logger.addHandler(self._file_logging)
            else:
                if self._file_logging:
                    self.logger.removeHandler(self._file_logging)
                    self._file_logging.close()
                    self._file_logging = None
        else:
            self.logger.debug('unknown: ', command, '=>', argument)

    def getConfiguration(self):
        return self._configuration

    def startSimulation(self):
        self._sendToConsole('running')

    def sendToConsole(self, command, argument):
        message = connector.Common.composeMessage(command, argument)
        self._sendToConsole('virtual_environment_to_console', message)

    def run(self):
        if not self._client.run():
            self.blenderVR.quit('Loosed the console')
        
    def _sendToConsole(self, command, argument = ''):
        try:
            self._client.send(command, argument)
        except socket.error:
            self.blenderVR.quit('Loosed the controller')
