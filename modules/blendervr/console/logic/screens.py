# -*- coding: utf-8 -*-
# file: blendervr/console/logic/screens.py

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

"""\
Screens set management for VR system.
"""


class ConsoleScreensLogic:
    """\
    Manage a set of screens corresponding to a VR system configuration.

    .. note:: 

        Real Screen objects construction is subcontracted to subclass
        via build_screen() method. This allow to create screen with mixin
        logic and GUI.

    :ivar _screens: mapping of screen name to Screen object.
    :type _screens: {'name':Screen}
    """
    def __init__(self):
        self._screens = {}

    def start(self):
        """\
        Begin the screens management… nothing to do.
        """
        pass

    def quit(self):
        """\
        Prepare the screens management to quit (quit all running screen).
        """
        self.quit_screen_by_names(self._screens.keys())

    def quit_screen_by_names(self, names):
        """\
        Force quit on screen(s) listed in names and remove them.

        :param names: sequence of screen names
        :type names: list / set / dict_keys / …
        """
        # Copy list in case someone gives a dict_keys view on self._screens.
        names = list(names)
        for name in names:
            if name in self._screens:
                self.logger.debug("Quitting screen", name)
                obj = self._screens[name]
                obj.quit()
                del self._screens[name]
                obj = None
            else:
                self.logger.warning("Require quit unknown screen %s", name)

    def set_screens(self, configurations, net_console, master_name,
                                                        port, complements):
        """\
        Prepare the screens for required configuration.

        No longer listed screen(s) are quit and removed.
        Missing screen(s) are created and referenced.
        All screen(s) are re-configured using ad-hoc configuration and complements.

        :param configurations: dictionnary of configuration dictionnaries, by screen name.
        :type configurations: {'name': {'confname':'confvalue'} }
        :param net_console: host and port to contact the console TCP server 'host:port'.
        :type net_console: string
        :param master_name: name of the master screen which manage scene graph modifications.
        :param master_name: string
        :param port: TCP port where the master will serve slaves synchronization.
        :type port: int
        :param complements: configuration complement for screens (not seen its usage).
        :type complements:
        """
        # Quit running screens which are no longer listed in configuration.
        current = set(self._screens.keys())
        futurs = set(configurations.keys())
        self.quit_screen_by_names(current - futurs)

        if len(configurations) == 0:
            self.update_gui()
            return

        # FIXED: This *logic* component previously built a mixed part (logic + GUI)
        # Screen object. this cannot work with bvr as a tool within Blender.
        # => moved Screen building code into derived mixed class method
        # (in blendervr.console.screens.ConsoleScreens class).
        for name, screenconf in configurations.items():
            # Build missing screens.
            if name not in self._screens:
                self.logger.debug("Creating screen", name)
                self._screens[name] = self.build_screen(self, name, net_console)
            # Prepare each screen with its own configuration.
            self.logger.debug("Configuring screen", name)
            self._screens[name].setConfiguration(screenconf, complements)

        #TODO : remove connexion and slaves !
        self._master_name = master_name
        self.get_master().setHierarchy({'port': port,
                                        'nodes': list(self._screens.keys())})

        slave_informations = {'port': port,
                              'master': self.get_master().getHostname()}
        for name, obj in self._screens.items():
            if name != self._master_name:
                obj.setHierarchy(slave_informations)
        obj = None

        self.update_gui()

        for name, obj in self._screens.items():
            self.logger.debug("Starting screen", name)
            obj.start()

    def get_master(self):
        """\
        Retrieve the ConsoleScreenLogic corresponding to master screen.
        """
        return self.getScreen(self._master_name)

    def getScreen(self, screen_name):
        """\
        Retrieve a ConsoleScreenLogic for a screen name.
        """
        return self._screens.get(screen_name, None)

    def getScreensNumber(self):
        """\
        Retrieve the count of screens.
        """
        return len(self._screens)

    def getStates(self):
        """\
        Return a general states counters by state.

        States are:

        - stopped
        - starting
        - building
        - runnnig

        :return: a count of screen in each state for each state
        :rtype: {'state':count}
        """
        states = {'stopped': 0,
                  'starting': 0,
                  'building': 0,
                  'running': 0}
        for name, obj in self._screens.items():
            states[obj.get_blender_player_state()] += 1
        return states

    def adapt_simulation_files_to_screen(self, loader_file,
                                         blender_file, processor_files):
        """\
        """
        for name, obj in self._screens.items():
            obj.adapt_simulation_files_to_screen(loader_file, blender_file,
                                                            processor_files)

    def start_simulation(self):
        """\
        """
        for name, obj in self._screens.items():
            obj.set_BlenderVR_state(True)

    def stop_simulation(self):
        """\
        """
        for name, obj in self._screens.items():
            if name != self._master_name:
                obj.set_BlenderVR_state(False)
        import time
        time.sleep(0.5)
        self.get_master().set_BlenderVR_state(False)

    def send_to_blender_player(self, command, message):
        """\
        """
        self.get_master().send_to_blender_player(command, message)

# Keep compatibility.
Logic = ConsoleScreensLogic
