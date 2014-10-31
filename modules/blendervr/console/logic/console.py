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

import socket
import os
from .. import exceptions
from ...tools.connector import Common
import copy
import select
import sys
import subprocess

class Logic:
    def __init__(self):
        self._possibleScreenSets = None
        self._anchor             = None
        self._previous_state     = None
        self._common_processors  = []

    def start(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port   = 31415
        while True:
            try:
                self._server.bind(('', self._port))
                break
            except socket.error:
                self._port += 1
        self._server.listen(10)
        self._server_listen_tag = self.addListenTo(self._server.fileno(), self._connect_client)
        from ... import version
        self.logger.info('blenderVR version:', version)

    def quit(self):
        pass

    def load_configuration_file(self):
        try:
            configuration_file = self.profile.getValue(['config', 'file'])
            if configuration_file is None:
                return
            configuration_paths = copy.copy(self.profile.getValue(['config', 'path']))

            configuration_path = os.path.dirname(configuration_file)
            # Don't remove the path from the configuration file, otherwise, other paths will be prioritaries !
            # configuration_file = os.path.basename(configuration_file)

            if configuration_paths is None:
                configuration_paths = [configuration_path]
            elif configuration_path not in configuration_paths:
                configuration_paths.append(configuration_path)

            previous_common_processors = self._common_processors

            from .. import xml
            config              = xml.Configure(self, configuration_paths, configuration_file)
            self._configuration = config.getConfiguration()

            starter            = self._configuration['starter']
            self._net_console  = starter['hostname'] + ':' + str(self._port)
            self._anchor       = starter['anchor']
            self._screenSets   = starter['configs']
            self._blender_exe  = starter['blender']
            possibleScreenSets = list(self._screenSets.keys())

            self._common_processors = self._configuration['processors']

            if self._possibleScreenSets != possibleScreenSets:
                self._possibleScreenSets = possibleScreenSets
                self.display_screen_sets(self._possibleScreenSets)
            self.set_screen_set()

        except SystemExit:
            raise
        except exceptions.Main as error:
            self.logger.error(str(error))
        except:
            self.logger.log_traceback(False)

    def set_screen_set(self):
        current = self.profile.getValue(['screen', 'set'])
        if current is not None and current in self._screenSets:
            new_screens = {}
            configuration_screens   = self._configuration['screens']
            configuration_computers = self._configuration['computers']

            from ..  import screen

            screenSet      = self._screenSets[current]
            masterScreen   = screenSet[0]
            configurations = {}
            for screen_name in screenSet:
                if screen_name not in configuration_screens:
                    self.logger.warning('Cannot find ' + screen_name + ' as screen in configuration file !')
                    return

                computer_name = configuration_screens[screen_name]['computer']
                if computer_name not in configuration_computers:
                    self.logger.warning('Cannot find ' + computer_name + ' as computer in configuration file !')
                    return

                if screen_name == masterScreen and self._configuration['focus_master']:
                    configuration_screens[screen_name]['keep_focus'] = True
                else:
                    configuration_screens[screen_name]['keep_focus'] = False

                configurations[screen_name] = { 'screen':   configuration_screens[screen_name],
                                                'computer': configuration_computers[computer_name]}

            complements = {'users'      : self._configuration['users'],
                           'plugins'    : self._configuration['plugins'],
                           'processors' : self._configuration['processors']}
            self._screens.set_screens(configurations,
                                      self._net_console,
                                      masterScreen,
                                      self._configuration['port'],
                                      complements)
            self._update_status()
            self.update_user_files(True)

    def _update_status(self):
        states = self._screens.getStates()
        states['starting'] += states['building']
        del(states['building'])
        if states['stopped'] == self._screens.getScreensNumber():
            state = 'stopped'
        elif states['starting'] == self._screens.getScreensNumber():
            state = 'starting'
        elif states['running'] == self._screens.getScreensNumber():
            state = 'running'
        else:
            state = None
        self._display_status(state, states)
        if self._previous_state != state:
            if self._processor:
                if state == 'running':
                    self._processor.start()
                if state == 'stopped':
                    self._processor.stop()
            self._previous_state = state
            self.update_processor()

    def _connect_client(self, *args):
        conn, addr = self._server.accept()

        from ...tools.connector import Server
        client = Server(conn)

        module, screen_name = client.getClientInformation()

        screen = self._screens.getScreen(screen_name)
        if screen:
            screen.setNetworkClient(module, client, addr)
        return True

    def update_user_files(self, force = False):
        blender_file = self.profile.getValue(['files','blender'])

        processor_files = [self.profile.getValue(['files', 'processor'])] + self._common_processors
        if self._processor_files != processor_files:
            if self._processor:
                self._processor.quit()
                del(self._processor)
            try:
                from ...processor import _getProcessor
                processor = _getProcessor(processor_files, self.logger, self.profile.getValue(['debug', 'processor']))
                self._processor = processor(self) 
            except:
                if self.profile.getValue(['debug', 'processor']):
                    self.logger.log_traceback(False)
                self._processor = None
                processor_files = []

        if self._processor and self._processor.useLoader():
            command = [sys.executable, self._update_loader_script, '--', blender_file]
            if self.profile.getValue(['debug', 'executables']):
                self.logger.error('Get loader script name:', ' '.join(command))
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            for line in process.stdout:
                loader_file = line.decode('UTF-8').rstrip()
                break
        else:
            loader_file = blender_file

        if loader_file != self._loader_file or blender_file != self._blender_file or processor_files != self._processor_files or force:
            self._loader_file     = loader_file
            self._blender_file    = blender_file
            self._processor_files = processor_files

            from . import file_name
            loader_file     = file_name.FileName(self._loader_file, self._anchor)
            blender_file    = file_name.FileName(self._blender_file, self._anchor)
            processor_files = []
            for processor_file in self._processor_files:
                processor_files.append(file_name.FileName(processor_file, self._anchor))
            self._screens.adapt_simulation_files_to_screen(loader_file, blender_file, processor_files)

    def get_blender_player_state(self):
        state = self._screens.getStates()
        for state, number in state.items():
            if number == self._screens.getScreensNumber():
                return state
        return None
        
    def compile_BC(self):
        try:
            import compileall
            compileall.compile_dir(os.path.join(blenderVR_root, 'modules', 'blendervr'), quiet = True)
        except:
            self.logger.log_traceback(False)

    def start_simulation(self):
        if self.get_blender_player_state() == 'stopped':
            self.compile_BC()
            if self._processor.useLoader():
                self._update_loader()
            self._screens.start_simulation()

    def stop_simulation(self):
        if self.get_blender_player_state() == 'running':
            self._screens.getMaster().ask_blender_player_to_quit()
            self._kill_timer = self.addTimeout(500, self._kill_blender_players)
        else:
            self._kill_blender_players()

    def _kill_blender_players(self):
        if self.get_blender_player_state() != 'stopped':
            try:
                del(self._kill_timer)
            except:
                pass
            self._screens.stop_simulation()

    def sendToVirtualEnvironment(self, command, argument):
        if self.get_blender_player_state() != 'running':
            return False
        message = Common.composeMessage(command, argument)
        self._screens.send_to_blender_player('console_to_virtual_environment', message)

    def receivedFromVirtualEnvironment(self, message):
        if self._processor:
            command, argument = Common.decomposeMessage(message)
            self._processor.receivedFromVirtualEnvironment(command, argument)

    def _linkProcessorToBlenderFile(self):
        if self.profile.getValue(['files', 'link']):
            blender_file_name = self.profile.getValue(['files', 'blender'])
            if blender_file_name is not None:
                processor_file_name, ext = os.path.splitext(blender_file_name)
                if ext == '.blend':
                    processor_file_name += '.processor.py'
                    if self.profile.getValue(['files', 'processor']) != processor_file_name:
                        if not os.path.isfile(processor_file_name):
                            processor_file_name = os.path.join(blenderVR_root, 'modules', 'blendervr', 'processor', 'default.py')
                        self.profile.setValue(['files', 'processor'], processor_file_name)
                        self._force_processor_file(processor_file_name)
        self.update_user_files()


    def _update_loader(self):
        if not os.path.isfile(self._loader_file) or (os.path.getctime(self._blender_file) > os.path.getctime(self._loader_file)):
            if not os.path.isfile(self._loader_file):
                self.logger.debug('Creating loader')
            else:
                self.logger.debug('Updating loader')
            command = [self._blender_exe, '-b', '-P', self._update_loader_script, '--', self._blender_file]
            if self.profile.getValue(['debug', 'executables']):
                self.logger.error('Update loader scripe:', ' '.join(command))
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            for line in process.stderr:
                self.logger.debug(line.decode('UTF-8').rstrip())


