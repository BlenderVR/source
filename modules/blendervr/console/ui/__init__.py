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

import os
import sys
import time
from ...tools import controller
import importlib
from ..protocol import composeMessage
from ..protocol import decomposeMessage

class UI():
    def __init__(self, port, debug = False):
        self._port  = port

        from ...tools import logger
        self._logger = logger.getLogger('blenderVR')

        output_logger = logger.File('/tmp/output.log')
        self._default_logger = self._logger.addLoginWindow(output_logger, True)
        if debug:
            # Define connexions until the controller is running ...
            self._logger.setLevel('debug')

        from ...tools import controller
        try:
            self._controller = controller.Controller('localhost:' + str(self._port), 'UI')
        except ConnectionRefusedError:
            self.logger.warning('Cannot find the controller on localhost:' + str(self._port))
            sys.exit()

        self._commands = {}
        for moduleName in ['root', 'set', 'get', 'reload']:
            try:
                _class = moduleName[0].upper() + moduleName[1:]
                module = importlib.import_module('..protocol.' + moduleName, __name__)
                self._commands[moduleName] = getattr(module, _class)(self._controller)
            except:
                self.logger.log_traceback(False)
                pass
        
        self._quit = False

    def getCommands(self):
        return self._commands
        
    def start(self):
        from ... import version
        self.logger.info('blenderVR version:', version)

        try:
            from . import completer
            self._completer = completer.Completer(self)
        except ImportError:
            self.logger.log_traceback(False)
            self.logger.info('Readline module not available.')
        else:
            self.logger.debug('Readline module available.')

    def main(self):
        try:
            while not self._quit:
                try:
                    line = input('blenderVR: ')
                except (EOFError, KeyboardInterrupt):
                    self._quit = True
                else:
                    command = line.split()
                    if command[0] == 'exit':
                        self._quit = True
                        continue
                    _module = command[0]
                    if _module in self._commands:
                        del(command[0])
                    else:
                        _module = 'root'
                    _class  = self._commands[_module]
                    _method = command[0]
                    del(command[0])
                    if hasattr(_class, _method):
                        if len(command) > 0:
                            result = getattr(_class, _method)(*command)
                        else:
                            result = getattr(_class, _method)()
                        if _module == 'get':
                            command, argument = decomposeMessage(result[1])
                            print(str(command) + ': ' + str(argument))
                            if _method == 'screenSets' and hasattr(self, '_completer'):
                                self._completer.setScreenSets(argument)
                    else:
                        self.logger.info('Invalid command:', line)
        except controller.closedSocket as e:
            self.logger.warning(e)
        except (KeyboardInterrupt, SystemExit):
            return

    def quit(self):
        self._quit = True

    @property
    def logger(self):
        return self._logger

