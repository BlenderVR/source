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

class Logic:
    def __init__(self):
        self._screens = {}

    def start(self):
        pass

    def quit(self):
        self.set_screens({}, None, None, None, None)

    def set_screens(self, configurations, net_console, master_name, port, complements):
        to_remove = []
        for name in list(self._screens.keys()):
            if name not in configurations:
                obj = self._screens[name]
                obj.quit()
                del(self._screens[name])
                obj = None

        if len(configurations) == 0:
            self.update_gui()
            return

        from .. import screen

        for name, configuration in configurations.items():
            if name not in self._screens:
                self._screens[name] = screen.Screen(self, name, net_console)

        for name, configuration in configurations.items():
            self._screens[name].setConfiguration(configuration, complements)

        #TODO : remove connexion and slaves !
        self._master_name = master_name
        self.getMaster().setHierarchy({'port' : port,
                                       'nodes': list(self._screens.keys())})

        slave_informations = {'port'  : port,
                              'master': self.getMaster().getHostname()}
        for name, obj in self._screens.items():
            if name != self._master_name:
                obj.setHierarchy(slave_informations)
        obj = None

        self.update_gui()

        for name, obj in self._screens.items():
            obj.start()

    def getMaster(self):
        return self._screens[self._master_name]

    def getScreen(self, screen_name):
        if screen_name in self._screens:
            return self._screens[screen_name]
        return None

    def getScreensNumber(self):
        return len(self._screens)

    def getStates(self):
        states = {'stopped'  : 0,
                  'starting' : 0,
                  'building' : 0,
                  'running'  : 0}
        for name, obj in self._screens.items():
            states[obj.get_blender_player_state()] += 1
        return states

    def adapt_simulation_files_to_screen(self, loader_file, blender_file, processor_files):
        for name, obj in self._screens.items():
            obj.adapt_simulation_files_to_screen(loader_file, blender_file, processor_files)

    def start_simulation(self):
        for name, obj in self._screens.items():
            obj.set_blenderVR_state(True)

    def stop_simulation(self):
        for name, obj in self._screens.items():
            if name != self._master_name:
                obj.set_blenderVR_state(False)
        import time
        time.sleep(0.5)
        self.getMaster().set_blenderVR_state(False)

    def send_to_blender_player(self, command, message): 
        self.getMaster().send_to_blender_player(command, message)
