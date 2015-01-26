# -*- coding: utf-8 -*-
# file: blendervr/tools/logger.py

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

"""
Handle all the errors, warnings and debug info
"""

import logging
import sys
import pprint
import inspect
import traceback

verbosities = ['debug', 'info', 'warning', 'error', 'critical']

class Logger(logging.getLoggerClass()):

    # "Random" string to be sure that it will not be displayed by error
    STACK = "csdvkcjldsqkfhvkdsjb nkjsfdvsqkljhfvlkqd kjhxdf"
    EXCEPTION = "dcljnqsdlfkjncvqsljnvl ksdjnvlqjwncvlqnfdv"
    POSITION = "cklnfslkjhfdmc, dnlskdjhvlqkjfkvj"
    
    def __init__(self, name):
        super(Logger, self).__init__(name)

        from types import MethodType
        for verbosity in verbosities:
            setattr(self, verbosity, MethodType(self._process, verbosity))

    def getVerbosities(self):
        return verbosities

    def setLevel(self, verbosity):
        super(Logger, self).setLevel(self._getVerbosity(verbosity))

    def _process(self, verbosity, *messages):
        elements = []
        for message in messages:
            if message == self.EXCEPTION:
                elements.append(traceback.format_exc().strip())
                continue
            if (message == self.STACK) or (message == self.POSITION):
                stack = inspect.stack()
                if message == self.POSITION:
                    stack = [stack[1]]
                else:
                    stack.reverse()
                    stack = stack[:-1]
                entries = []
                for element in stack:
                    entry = 'File "' + element[1] + '", '
                    entry += 'line ' + str(element[2]) + ', '
                    entry += 'in ' + element[3]
                    if message != self.POSITION:
                        entry += "\n\t" + element[4][0].strip()
                    entries.append(entry)
                elements.append("\n".join(entries))
                continue
            if isinstance(message, (dict, tuple, list)):
                elements.append(pprint.pformat(message))
                continue
            elements.append(str(message))
        getattr(super(Logger, self), verbosity)(' '.join(elements))

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

class Handler(logging.Handler):
    def __init__(self, logger):
        logging.Handler.__init__(self)
        logger.addHandler(self)

    # TODO: implement flush element
    def flush(self):
        pass

    def _getLogFromRecord(self, record, context):
        return {'level':   record.levelno,
                'time':    record.created,
                'context': context,
                'message': record.msg}

class Network(Handler):
    def __init__(self, logger, connection, context):
        Handler.__init__(self, logger)
        self._connection = connection
        self._context    = context

    def emit(self, record):
        self._connection.send('logger', self._getLogFromRecord(record, self._context))

# Minimal logger on the screen. We can add formatter later, if we wish ...
class Console(Handler):
    def __init__(self, logger):
        Handler.__init__(self, logger)

    def emit(self, record):
        printLogOnConsole(record.levelno, record.msg)

streamMapping = {'DEBUG': sys.stdout,
                 'INFO': sys.stdout,
                 'WARNING': sys.stderr,
                 'ERROR': sys.stderr,
                 'CRITICAL': sys.stderr}

def printLogOnConsole(level, message):
    levelname = logging.getLevelName(level)
    if levelname in streamMapping:
        stream = streamMapping[levelname]
    else:
        stream = sys.stdout
    nb_return = message.count("\n")
    if nb_return > 2:
        stream.write('***********************************************\n')
    stream.write(levelname + ': ')
    if nb_return > 0:
        stream.write('\n')
    stream.write(message + '\n')
    if nb_return > 2:
        stream.write('***********************************************\n')
    stream.flush()

if not isinstance(logging.getLoggerClass(), Logger):
    logging.setLoggerClass(Logger)

def getLogger(name):
    return logging.getLogger(name)


# def getGUIHandler(login_window):
#     return handler
