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

class main(base.XML):

    def __init__(self, parent, name, attrs):
        super(main, self).__init__(parent, name, attrs)
        self._attribute_list += ['name', 'hostname']
        self._class_list     += ['system']

        if 'name' not in attrs:
            self.raise_error('Error: missing computer name for the computer');
        self._name = attrs['name']

        if 'hostname' not in attrs:
            self.raise_error('Error: missing hostname for the computer')
        self._hostname = attrs['hostname']
        if self._hostname.strip() == '*':
            import socket
            self._hostname = socket.gethostname()

        self._system = None

        self._parent._addComputer(self._name, self)

    def _getChildren(self, name, attrs):
        if name == 'system':
            from . import system
            self._system = system.XML(self, name, attrs)
            return self._system
        return super(main, self)._getChildren(name, attrs)

class container(base.XML):

    def __init__(self, parent, name, attrs):
        super(container, self).__init__(parent, name, attrs)

    def _getChildren(self, name, attrs):
        if name == 'computer':
            return main(self, name, attrs)
        if name == 'system':
            from . import system
            self._system = system.XML(self, name, attrs)
            return self._system
        return super(container, self)._getChildren(name, attrs)

    def _addComputer(self, name, computer):
        self._parent._add('computers', name, computer)
