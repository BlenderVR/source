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

import sys
import os
from . import common_system
from . import base

class blenderplayer(base.single):
    def __init__(self, parent, name, attrs):
        super(blenderplayer, self).__init__(parent, name, attrs)
        self._attribute_list += ['executable', 'environments']
        if 'executable' in attrs:
            self._executable = attrs['executable']
        else:
            self._executable = None
        self._environments = None

    def characters(self,string):
        if self._inside == 'environment':
            self._setEnvironment(string)

    def _default(self):
        super(blenderplayer, self)._default()
        if self._executable is None:
            if sys.platform == 'win32':
                blender_program = "blenderplayer.exe"
            else:
                blender_program = "blenderplayer"
            self._executable = self.which(blender_program)
        if self._environments is None:
            self._environments = {}

class daemon(base.single):
    def __init__(self, parent, name, attrs):
        super(daemon, self).__init__(parent, name, attrs)
        self._attribute_list += ['environments', 'transmit']
        self._environments = None
        self._transmit = False
        if 'transmit' in attrs:
            self._transmit = self.getBoolean(attrs['transmit'])

    def characters(self,string):
        if self._inside == 'environment':
            self._setEnvironment(string)

    def _default(self):
        super(daemon, self)._default()
        if self._environments is None:
            self._environments = {}

class log(base.alone):
    def __init__(self, parent, name, attrs):
        super(log, self).__init__(parent, name, attrs)
        self._attribute_list += ['clear_previous', 'path']

        if 'clear_previous' in attrs:
            self._clear_previous = self.getBoolean(attrs['clear_previous'])
        else:
            self._clear_previous = None

        if 'path' in attrs:
            self._path = attrs['path']
        else:
            self._path = None

    def _default(self):
        super(log, self)._default()
        if self._clear_previous is None:
            self._clear_previous = True
        if self._path is None:
            self._path = os.path.join(os.path.expanduser('~'), '.log', 'blender')

class login(base.alone):
    def __init__(self, parent, name, attrs):
        super(login, self).__init__(parent, name, attrs)
        self._attribute_list += ['remote_command', 'python']

        if 'remote_command' in attrs:
            self._remote_command = attrs['remote_command']
        else:
            self._remote_command = None

        if 'python' in attrs:
            self._python = attrs['python']
        else:
            self._python = None

    def _default(self):
        super(login, self)._default()
        if self._remote_command is None:
            self._remote_command = ''
        if self._python is None:
            self._python = sys.executable
    
class XML(common_system.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._attribute_list += ['root']
        self._class_list     += ['blenderplayer', 'daemon', 'log', 'login']
        if 'root' in attrs:
            self._root = attrs['root']
        else:
            self._root = None
        self._blenderplayer = None
        self._daemon        = None
        self._log           = None
        self._login         = None

    def _getChildren(self, name, attrs):
        if name == 'blenderplayer':
            self._blenderplayer = blenderplayer(self, name, attrs)
            return self._blenderplayer
        if name == 'daemon':
            self._daemon = daemon(self, name, attrs)
            return self._daemon
        if name == 'log':
            self._log = log(self, name, attrs)
            return self._log
        if name == 'login':
            self._login = login(self, name, attrs)
            return self._login
        return super(XML, self)._getChildren(name, attrs)

    def _default(self):
        super(XML, self)._default()
        if self._root is None:
            self._root = blenderVR_root
