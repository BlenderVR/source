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
from . import exceptions

STATE_FREE    = 0
STATE_PRESS   = 1
STATE_ACTIVE  = 2
STATE_RELEASE = 3

class Base(base.Base):
    def __init__(self, parent, configuration):
        super(Base, self).__init__(parent)

class Receiver(Base):
    def __init__(self, main, configuration):
        super(Receiver, self).__init__(main, configuration)
        self._name = configuration['device']
        self._host = configuration['host']

    def __str__(self):
        return self._name + "@" + self._host

    def run(self):
        self._connexion.mainloop()

class Sender(Base):

    def __init__(self, main, configuration):
        super(Sender, self).__init__(main, configuration)
        self._processor_method_name = configuration['processor_method']
        try:
            self._data = configuration['data']
        except KeyError:
            self._data = None
        self._users = []
        if 'users' in configuration and configuration['users'] is not None:
            try:
                self._users.append(self.blenderVR.getUserByName(configuration['users']))
            except exceptions.User:
                raise exceptions.Processor_Invalid_Device('user not found for processor "' + configuration['processor_method'] + '": ' + configuration['users'])
        else:
            self._users = list(self.blenderVR.getAllUsers().values())

    def checkMethod(self, display_missing):
        processor = self.blenderVR.getProcessor()
        if not hasattr(processor, self._processor_method_name):
            if display_missing:
                self.logger.warning('processor does not have "' + self._processor_method_name + '" method')
            return False 
        if display_missing:
            self.logger.info('using processor method: "' + self._processor_method_name + '"')
        self._processor_method = getattr(processor, self._processor_method_name)
        return True

    def process(self, info):
        info['users'] = self._users
        info['data']  = self._data
        info['self']  = self
        self._processor_method(info)
