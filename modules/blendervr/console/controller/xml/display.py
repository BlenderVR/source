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

from . import reusable
from . import base

class graphic_buffer(base.mono):
    def __init__(self, parent, name, attrs):
        super(graphic_buffer, self).__init__(parent, name, attrs)
        self._attribute_list += ['buffer', 'user', 'eye']

        if 'buffer' in attrs:
            self._buffer = attrs['buffer'].lower()
        else:
            self._buffer = 'mono'
        if self._buffer not in {'mono', 'right', 'left'}:
            self.raise_error('Invalid graphic_buffer buffer (' + str(self._buffer) + ') : must be one of mono, right or left')

        if 'eye' in attrs:
            self._eye = attrs['eye'].lower()
        else:
            self._eye = 'middle'
        if self._eye not in {'middle', 'right', 'left'}:
            self.raise_error('Invalid graphic_buffer eye (' + str(self._eye) + ') : must be one of middle, right or left')

        if 'user' in attrs:
            self._user = attrs['user']
        else:
            self._user = None


class XML(reusable.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._attribute_list += ['options', 'viewport', 'environments']
        self._class_list     += ['graphic_buffer']
        self._graphic_buffer  = None
        self._viewport        = None
        self._environments    = None

        if 'options' in attrs:
            self._options = attrs['options']
        else:
            self._options = None

        self._inside          = None

    def _getChildren(self, name, attrs):
        for element in {'viewport', 'environment'}:
            if name == element:
                if self._inside is not None:
                    self.raise_error('Cannot import ' + str(name) + ' inside ' + str(self._inside) + ' !')
                self._inside = name
                return None
        if name == 'graphic_buffer':
            graph_buf = graphic_buffer(self, name, attrs)
            if self._graphic_buffer is None:
                self._graphic_buffer = []
            self._graphic_buffer.append(graph_buf)
            return graph_buf
        return super(XML, self)._getChildren(name, attrs)

    def characters(self, string):
        if self._inside == 'viewport':
            self._viewport = self.getVector(string, 4, 0.0)
        elif self._inside == 'environment':
            self._setEnvironment(string)

    def endElement(self, name):
        if self._inside:
            self._inside = None
            return
        super(XML, self).endElement(name)
