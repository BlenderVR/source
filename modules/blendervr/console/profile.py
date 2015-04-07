# -*- coding: utf-8 -*-
# file: blendervr/console/profile.py

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

import pickle
import os
import copy


class Profile:
    def __init__(self, configuration_file):
        self._configuration_file = configuration_file
        self._lock = False

        try:
            with open(self._configuration_file, 'rb') as node:
                self._data = pickle.load(node)
        except:
            self._data = {'root': BlenderVR_root}
            self._write()

    def lock(self, lock):
        self._lock = lock

    def dump(self):
        import pprint
        pprint.pprint(self._data)

    def setDefault(self, default, node=None, root=None):
        if root is not None:
            root = self._normalizeIndex(root)
            current = self.getValue(root)
            if current is None:
                self.setValue(root, default)
                return
            if isinstance(current, dict):
                node = eval(self._getArrayElementByIndex(root))
            else:
                return
        if node is None:
            node = self._data
        for key, value in default.items():
            if key not in node:
                node[key] = copy.copy(value)
                continue
            if isinstance(node[key], dict) and isinstance(value, dict):
                self.setDefault(value, node[key])
                continue
        self._write()

    def _write(self):
        path_name = os.path.dirname(self._configuration_file)
        if not os.path.isdir(path_name):
            os.makedirs(path_name)
        with open(self._configuration_file, 'wb') as node:
            pickle.dump(self._data, node)

    def _getArrayElementByIndex(self, index):
        return "self._data['" + ("']['").join(index) + "']"

    def _normalizeIndex(self, index):
        if isinstance(index, str):
            return [index]
        return index
        result = []
        for sub_index in index:
            normalized_name = ''
            for char in str(sub_index):
                if not char.isalnum():
                    char = "_%x" % ord(char)
                normalized_name += char
            result.append(normalized_name)
        return result

    def setValue(self, index, value, write=True):
        if self._lock:
            return
        index = self._normalizeIndex(index)
        try:
            if index[0] not in self._data:
                self._data[index[0]] = {}
            cumul = [index[0]]
            for cur in index[1:-1]:
                if cur not in eval(self._getArrayElementByIndex(cumul)):
                    exec(self._getArrayElementByIndex(cumul)
                                        + "['" + cur + "'] = {}")
                cumul.append(cur)
            var = self._getArrayElementByIndex(index)
            if value is None:
                exec('del(' + var + ')')
            if isinstance(value, bool):
                exec(var + "='" + str(value) + "'")
            if isinstance(value, str):
                exec(var + "='" + value + "'")
            elif isinstance(value, (int, float, bool, dict, list, tuple)):
                exec(var + "=" + str(value))
        except:
            pass
        if write:
            self._write()

    def getValue(self, index):
        index = self._normalizeIndex(index)
        try:
            result = eval(self._getArrayElementByIndex(index))
            return result
        except:
            return None

    def appendValue(self, index, value, write=True):
        previous = self.getValue(index)
        if not isinstance(previous, (list, tuple)):
            previous = [previous]
        if isinstance(value, (list, tuple)):
            current = previous + value
        else:
            current = previous + [value]
        self.setValue(index, current, write)

    def prependValue(self, index, value, write=True):
        previous = self.getValue(index)
        if not isinstance(previous, (list, tuple)):
            previous = [previous]
        if isinstance(value, (list, tuple)):
            current = value + previous
        else:
            current = [value] + previous
        self.setValue(index, current, write)
