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
from .. import xml

class XML(xml.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._class_list += ['library']
        self._library = None

    def _getChildren(self, name, attrs):
        if name == 'library':
            self._library = Library(self, name, attrs)
            return self._library

        return super(XML, self)._getChildren(name, attrs)

class Library(xml.mono):
    def __init__(self, parent, name, attrs):
        super(Library, self).__init__(parent, name, attrs)
        self._attribute_list += ['folder']

        if 'folder' not in attrs:
            self.raise_error("Occulus Rift Library must have a folder !")
        else:
            folder = attrs['folder']

            if not os.path.exists(folder):
                self.raise_error("Library folder \"{0}\" doesn't exist !".format(folder))
            elif not os.path.isdir(folder):
                self.raise_error("Library folder \"{0}\" is not a directory !".format(folder))
            else:
                try:
                    import sys
                    sys.path.append(folder)
                    from game_engine_rift.rift import PyRift
                    assert PyRift     # avoid import unused
                    sys.path.remove(folder)
                except ImportError:
                    self.logger.info('No Occulus Rift python module available. Expected \"game_engine_rift\" package in \"{0}\" folder'.format(folder))
                else:
                    self._folder = folder
