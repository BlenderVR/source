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

from .common import Common
from types import MethodType
import glob
import os

class Simple(Common):
    def __init__(self, protocol, path_completion = []):
        self._protocol = protocol
        Common.__init__(self, self._protocol.getConnection())

        self._cmd_methods = []
        for action in dir(self._protocol):
            if action.startswith('_'):
                continue
            self._cmd_methods.append('do_' + action)
            setattr(self, 'do_' + action, MethodType(self._do, action))
            if hasattr(getattr(self._protocol, action), '__doc__'):
                self._cmd_methods.append('help_' + action)
                setattr(self, 'help_' + action, MethodType(self._help, action))
            if action in path_completion:
                self._cmd_methods.append('complete_' + action)
                setattr(self, 'complete_' + action, self._path_completion)

    # Overloading of this method to add our own methods
    def get_names(self):
        return self._cmd_methods

    def _do(self, action, *args):
        if hasattr(self._protocol, action):
            getattr(self._protocol, action)(args)

    def _help(self, action):
        help(getattr(self._protocol, action))

    def _path_completion(self, text, line, begidx, endidx):
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            if path and os.path.isdir(path) and path[-1] != os.sep:
                path += os.sep
            completions.append(path.replace(fixed, "", 1))
        return completions
            
