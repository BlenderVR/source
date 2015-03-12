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

class Screens(base.Base):
    def __init__(self, parent):
        base.Base.__init__(self, parent)
        self._screens = {}

    def setConfiguration(self, configuration, complements, port):
        # TODO: use list difference instead of scanning ...
        for name in list(self._screens.keys()):
            if name not in configurations:
                obj = self._screens[name]
                obj.quit()
                del(self._screens[name])
                obj = None

        from . import screen
        self._master_name = None
        for name, configuration in configuration.items():
            if not self._master_name:
                self._master_name = name
            if name not in self._screens:
                self._screens[name] = screen.Screen(self, name)
            self._screens[name].setConfiguration(configuration, complements)

        #TODO : remove connexion and slaves !
        self.getMaster().setHierarchy({'port' : port,
                                       'nodes': list(self._screens.keys())})

        slave_informations = {'port'  : port,
                              'master': self.getMaster().getHostname()}
        for name, obj in self._screens.items():
            if name != self._master_name:
                obj.setHierarchy(slave_informations)
        obj = None

    def getMaster(self):
        return self._screens[self._master_name]

    def __del__(self):
        del(self._screens)

    def appendClient(self, client):
        name = client.getName()
        if name in self._screens:
            self._screens[name].appendClient(client)

    def runAction(self, action, element):
        for name, obj in self._screens.items():
            obj.runAction(action, element)

    def adapt_simulation_files_to_screen(self, loader_file, blender_file, processor_files):
        for name, obj in self._screens.items():
            obj.adapt_simulation_files_to_screen(loader_file, blender_file, processor_files)
