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
from ...tools import controller
import importlib
from ..protocol import composeMessage
from ..protocol import decomposeMessage
from .. import Console

class UI(Console):
    def __init__(self, port, min_log_level, log_in_file):
        Console.__init__(self, min_log_level, log_in_file)

        self._port  = port
        self._print = lambda *args: True

        try:
            self._controller = controller.Controller('localhost:' + str(self._port), 'UI')
        except ConnectionRefusedError:
            self.logger.warning('Cannot find the controller on localhost:' + str(self._port))
            sys.exit()

        self._commands = {}
        for moduleName in ['root', 'set', 'get', 'reload', 'status', 'action', 'debug']:
            try:
                _class = moduleName[0].upper() + moduleName[1:]
                module = importlib.import_module('..protocol.' + moduleName, __name__)
                if moduleName == 'action':
                    self._commands['start'] = getattr(module, _class)(self._controller, 'start')
                    self._commands['stop'] = getattr(module, _class)(self._controller, 'stop')
                else:
                    self._commands[moduleName] = getattr(module, _class)(self._controller)
            except:
                self.logger.log_traceback(False)
                pass
        
        self._quit = False

        # initialize the screen sets !
        self.process(self._commands['get'], 'screenSets')

        self._print = lambda *args: print(*args)

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
                    try:
                        _method = command[0]
                        del(command[0])
                    except IndexError:
                        _method = '_default'
                    if not self.process(_class, _method, *command):
                        self.logger.info('Invalid command:', line)
        except controller.closedSocket as e:
            self.logger.warning(e)
        except (KeyboardInterrupt, SystemExit):
            return

    def process(self, _class, _method, *arguments):
        if hasattr(_class, _method):
            try:
                result = getattr(_class, _method)(*arguments)
            except TypeError:
                print('Invalid arguments:', arguments)
                return True
            if result != None:
                self._print(str(_method) + ': ' + str(result))
                if _method == 'screenSets' and hasattr(self, '_completer'):
                    self._completer.setScreenSets(result)
            return True
        return False

    def quit(self):
        self._quit = True
