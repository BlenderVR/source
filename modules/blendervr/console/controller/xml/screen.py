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
        self._attribute_list += ['name', 'computer', 'device_type']
        self._class_list     += ['display']

        if 'name' not in attrs:
            self.raise_error('Error : missing screen name !')
        self._name = attrs['name']

        if 'computer' not in attrs:
            self.raise_error('Error : missing computer name of the screen !')
        self._computer = attrs['computer']

        self.device_type = None
        self._display    = None

        self._parent._addScreen(self._name, self)

    def _getChildren(self, name, attrs):
        if name == 'display':
            from . import display
            self._display = display.XML(self, name, attrs)
            return self._display

        from . import device
        device_object = device.getDevice(self, name, attrs)
        if device_object:
            setattr(self, '_' + name, device_object)
            self._device_type = name
            self._class_list += [name]
            return device_object

        return super(main, self)._getChildren(name, attrs)

class container(base.XML):

    def __init__(self, parent, name, attrs):
        super(container, self).__init__(parent, name, attrs)

    def _getChildren(self, name, attrs):
        if name == 'screen':
            return main(self, name, attrs)
        if name == 'display':
            from . import display
            self._display = display.XML(self, name, attrs)
            return self._display
        return super(container, self)._getChildren(name, attrs)

    def _addScreen(self, name, screen):
        self._parent._add('screens', name, screen) 
