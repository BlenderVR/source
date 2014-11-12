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

import logging
import sys
import pprint

verbosities = ['debug', 'info', 'warning', 'error', 'critical']

class Logger(logging.getLoggerClass()):

    def __init__(self, name):
        super(Logger, self).__init__(name)

        from types import MethodType
        for verbosity in verbosities:
            setattr(self, verbosity, MethodType(self._process, verbosity))

    def getVerbosities(self):
        return verbosities

    def setLevel(self, verbosity):
        super(Logger, self).setLevel(self._getVerbosity(verbosity))

    def log_traceback(self, error):
        if error:
            method = self.error
        else:
            method = self.warning
        try:
            import traceback
            result = traceback.format_exc()
            method('***************************')
            method(result)
            method('***************************')
        except:
            import inspect
            self.debug('***************************')
            stack = inspect.stack()
            stack.reverse()
            for element in stack:
                self.debug('File "' + element[1] + '", line ' + str(element[2]) + ', in', element[3], "\n", element[4][0].rstrip())
            self.debug('***************************')

    def get_position(self):
        import inspect
        stack = inspect.stack()
        element = stack[1]
        return 'File "' + element[1] + '", line ' + str(element[2]) + ', in', element[3]

    def log_position(self): 
        import inspect
        stack = inspect.stack()
        element = stack[1]
        self.debug('File "' + element[1] + '", line ' + str(element[2]) + ', in', element[3])

    def _process(self, verbosity, sep=' ', *messages):
        elements = []
        for message in messages:
            if isinstance(message, (dict, tuple, list)):
                elements.append(pprint.pformat(message))
            else:
                elements.append(str(message))
        for message in (sep.join(elements)).rsplit('\n'):
            getattr(super(Logger, self), verbosity)(message)

    def _getVerbosity(self, verbosity):
        if verbosity is not None:
            verbosity = verbosity.lower()

        if verbosity == 'debug':
            return logging.DEBUG
        if verbosity == 'info':
            return logging.INFO
        if verbosity == 'warning':
            return logging.WARNING
        if verbosity == 'error':
            return logging.ERROR
        if verbosity == 'critical':
            return logging.CRITICAL

        return logging.WARNING

    def addLoginWindow(self, login_window, addName = False):
        handler = logging.StreamHandler(login_window)
        if addName:
            handler.setFormatter(logging.Formatter('%(levelname)s> %(asctime)s [%(name)s] %(message)s'))
        else:
            handler.setFormatter(logging.Formatter('%(levelname)s> %(asctime)s %(message)s'))
        self.addHandler(handler)
        return handler

class Console:
    def __init__(self):
        self._mapping = {'DEBUG'    : sys.stdout,
                         'INFO'     : sys.stdout,
                         'WARNING'  : sys.stderr,
                         'ERROR'    : sys.stderr,
                         'CRITICAL' : sys.stderr}

    def write(self, *messages):
        elements = []
        elements = []
        for message in messages:
            elements.append(str(message))
        for message in (' '.join(elements)).split('\n'):
            message = message.rstrip(' \n\r')
            if len(message) > 0:
                message_type = message.split('>')
                message_type = message_type[0]
                if message_type in self._mapping:
                    dest = self._mapping[message_type]
                    dest.write('Console logger: ' + message + '\n')
                    dest.flush()
            

if not isinstance(logging.getLoggerClass(), Logger):
    logging.setLoggerClass(Logger)

def getLogger(name):
    return logging.getLogger(name)

# def getGUIHandler(login_window):
#     return handler
