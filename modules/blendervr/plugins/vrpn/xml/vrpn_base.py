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

from ... import xml

class Receiver(xml.XML):

    def __init__(self, parent, name, attrs):
        super(Receiver, self).__init__(parent, name, attrs)
        self._attribute_list += ['device', 'host']

        if 'device' not in attrs:
            self.raise_error('VRPN receiver requires a device !')
        self._device = attrs['device']

        if 'host' not in attrs:
            self.raise_error('VRPN receiver requires a host !')
        self._host = attrs['host']

class Sender(xml.XML):

    def __init__(self, parent, name, attrs):
        super(Sender, self).__init__(parent, name, attrs)
        self._attribute_list += ['processor_method', 'users', 'data']

        if 'processor_method' not in attrs:
            self.raise_error('VRPN sender requires a process method !')
        self._processor_method = attrs['processor_method']

        if 'users' in attrs:
            self._users = attrs['users']
        else:
            self._users = None

        if 'data' in attrs:
            self._data = attrs['data']
        else:
            self._data = None
