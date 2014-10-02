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

from . import exceptions
from .. import base
import struct

def getString(value):
    result = bytes(value, 'latin1')
    for i in range(0, 4 - (len(result) % 4)):
        result += b'\x00'
    return result
    

class MSG(base.Base):
    def __init__(self, parent, command):
        super(MSG, self).__init__(parent)
        self._command   = command
        self._arguments = b''
        self._types     = ','

    def append(self, argument):
        if isinstance(argument,dict):
            argument = list(argument.items())
        if hasattr(argument, '__iter__') and not type(argument) in (str,bytes):
            for arg in argument:
                self.append(arg)
            return
        
        if type(argument) in [float]:
            self._arguments += struct.pack(">f", float(argument))
            self._types     += 'f'
        elif type(argument) in [int]:
            self._arguments += struct.pack(">i", int(argument))
            self._types     += 'i'
        elif type(argument) in [bool]:
            self._arguments += struct.pack(">i", int(argument))
            self._types     += 'i'
        elif type(argument) in [str]:
            self._arguments += getString(argument)
            self._types     += 's'
        else:
            raise exceptions.OSC_Invalid_Type(str(type(argument)) + ' unknown type')

    def getBinary(self):
        return getString(self._command) + getString(self._types) + self._arguments
