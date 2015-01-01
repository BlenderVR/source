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
import importlib

class XML(base.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._class_list     += ['computers', 'screens', 'users', 'processors', 'starter', 'plugins']
        self._attribute_list += ['port', 'focus_master']
        self._computers       = None
        self._screens         = None
        self._users           = None
        self._processors      = None
        self._starter         = None

        if 'port' in attrs:
            self._port = attrs['port']
        else:
            self._port = '2731'
        if 'focus_master' in attrs:
            self._focus_master = self.getBoolean(attrs['focus_master'])
        else:
            self._focus_master = False

    def _add(self, name, node_name, node_obj):
        _name = '_' + name
        if getattr(self, _name) is None:
            setattr(self, _name, {})
        if node_name in getattr(self, _name):
            self.raise_error(name + ' already defined in configuration ' + name + ' !')
        getattr(self, _name)[node_name] = node_obj

    def _getChildren(self, name, attrs):
        for module_name in ('system', 'display', 'behaviour', 'starter', 'processors', 'plugins'):
            if name == module_name:
                module = importlib.import_module('..'+module_name, __name__)
                setattr(self, '_'+module_name, module.XML(self, name, attrs))
                return getattr(self, '_'+module_name)

        for module_name in ('computer', 'screen', 'user'):
            if name == module_name+'s':
                module = importlib.import_module('..'+module_name, __name__)
                return  module.container(self, name, attrs)
