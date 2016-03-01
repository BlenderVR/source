# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# file: blendervr/console/console.py

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
import threading
import sys
import os
import logging
from . import argument as argument_handler

class UI(argument_handler.Argument_handler):

    def __init__(self, parent=None):
        self._arg = None
        self.thread_state="running"
        self._stop=False
        argument_handler.Argument_handler.__init__(self)
        return

    def main(self):
        self.print_header()
        if not self.start_mode:
            self.terminal_mode()
        else:
            self._start_mode()

    #Called when program is in terminal mode
    def terminal_mode(self):
        self.load_configuration_file()
        self._linkProcessorToBlenderFile()

        print("FOR HELP WRITE -h OR --help")

        while not self._stop:
            argument = self.get_argument()
            argument = argument.split(" ")
            if argument[0] == "exit":
                self.stop()
            else:
                argument_handler.Argument_handler.main(self, argument)
                self._arg=None

    #call if the program is on-the-fly render mode. All the data is already entered. Start the simulation with the data entered
    def _start_mode(self):

        #CONSTANTS FOR EACH FILE
        CONFIG = 0
        BLENDER = 1
        PROCESSOR = 2
        SCREEN = 3

        #check for the configuration file, and check if it's valid. if it isn't kill the program. if it is load it and continue
        if os.path.isfile(self.launch_data[CONFIG]) and self.launch_data[CONFIG].endswith('.xml') \
                and self.change_config_file(self.launch_data[CONFIG], self.launch_data[SCREEN], True):

            #if the screen set is in the possible screen sets, change it. If it isn't kill program
            if self.launch_data[SCREEN] in self._possibleScreenSets and \
                    self.change_screen(self.launch_data[SCREEN]):

                #if the blender file is valid, load blender file. else kill the program
                if os.path.isfile(self.launch_data[BLENDER]) and self.launch_data[BLENDER].endswith('.blend') and \
                    self.change_blender_file(self.launch_data[BLENDER]):

                        #if processor file is valid load, else kill
                        if os.path.isfile(self.launch_data[PROCESSOR]) and self.launch_data[PROCESSOR].endswith('.py') and \
                                self.change_processor_file(self.launch_data[PROCESSOR]):

                            #Wait for all the daemons
                            daemons_started = False

                            #Can be stopped with Keyboard Interrupt
                            print("Waiting for daemons to start...")
                            try:
                                while not daemons_started:
                                    daemons_started = True
                                    for name, screen in self._screens.getScreens():
                                        #if daemon isn't running check again
                                        if not screen.daemon_is_running():
                                            daemons_started = False

                                print("Daemon Started!!!")
                                print("Starting Simulation...")

                                self.start_simulation()

                                #While the simulation is running, keep the program alive
                                while not self.state.endswith("stopped"):
                                    import time
                                    time.sleep(5)

                            except KeyboardInterrupt:
                                pass
                            except SystemExit:
                                pass

                        else:
                            self.logger.critical("Processor file not valid")
                else:
                    self.logger.critical("Blender File isn't valid")
            else:
                self.logger.critical("Screen set " + self.launch_data[SCREEN] +  " isn't valid")
        else:
            self.logger.critical("Config file " + self.launch_data[CONFIG] + " isn't a valid config file")
        self.stop()

    def stop(self):
        self._stop = True
        self.thread_state = "stopped"
    #header
    def print_header(self):
        print('**********************************************************')
        print('        BlenderVR Copyright (C) LIMSI-CNRS (2014)')
        print('**********************************************************')


    def get_argument(self):
        '''TODO: The input works, but because there's some output coming from other threads, the ">>" isn't always
               in sync with the cursor. It is especially noticeable at the beginning of the application, when it isn't
               in silent mode, the message "Daemon for screen 'x' started" is below the ">>". I tried to fix it in the CustomPrint
               class but it wasn't working. '''
        import readline
        return input(">> ")


    def complete(self, text, state):
        pass

    #initializes the logger in the console. It adds a streamhandler to the logger.
    def initialize_console_logger(self):
        #create stdout handler for the logger
        handler = logging.StreamHandler(sys.stdout)

        #create formatter for the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:    %(message)s')
        handler.setFormatter(formatter)

        self._logger.addHandler(handler)

        print("Current level of the logger: " + self.log_level)
        self._logger.setLevel(self.log_level)

    def get_state(self):
        return self.thread_state
