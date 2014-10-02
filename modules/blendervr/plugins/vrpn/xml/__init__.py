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
from ... import xml
import importlib

class XML(xml.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._device_types    = ['analog', 'button', 'text', 'tracker']
        self._attribute_list  = ['floor', 'display_processors']

        if 'display_processors' in attrs:
            self._display_processors = self.getBoolean(attrs['display_processors'])
        else:
            self._display_processors = None

        self._floor           = None

        self._analog          = None
        self._button          = None
        self._text            = None
        self._tracker         = None

    def _getChildren(self, name, attrs):
        for module_name in self._device_types:
            if name == module_name:
                module = importlib.import_module(__name__ + '.' + module_name)
                _class = module.XML(self, name, attrs)
                if getattr(self, '_' + module_name) is None:
                    setattr(self, '_' + module_name, [])
                    self._class_list.append(module_name)
                getattr(self, '_' + module_name).append(_class)
                return _class
        if name == 'floor':
            self._floor = self.getVector(attrs, 3, 0.0)
            return None
        return super(XML, self)._getChildren(name, attrs)

    def _default(self):
        super(XML, self)._default()
        if self._floor is None:
            self._floor = self.getVector('0.0, 0.0, 0.0', 3, 0.0)
        if self._display_processors is None:
            self._display_processors = False
