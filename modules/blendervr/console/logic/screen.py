# -*- coding: utf-8 -*-
# file: blendervr/console/logic/screen.py

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
import subprocess
import sys
#import socket
import copy
import shlex


class Logic:
    def __init__(self, net_console):
        self._net_console = net_console
        self._process = None

        self._clients = {'daemon': None,
                         'blender_player': None}

        self._stop = False
        self._state = 'stopped'

    def __del__(self):
        pass

    def start(self):
        if not self.daemon_is_running():
            self._startDaemon()

    def quit(self):
        self._stop = True
        if self._clients['daemon']:
            self._clients['daemon'].send('kill daemon')
        self._close_network_client(self._clients['blender_player'])
        self._close_network_client(self._clients['daemon'])
        self._stopDaemon()

    def restartDaemon(self):
        if self._clients['daemon']:
            self._clients['daemon'].send('kill daemon')

    def setConfiguration(self, configuration, complements):
        screen_conf = configuration['screen']
        computer_conf = configuration['computer']
        system = computer_conf['system']

        self._complements = complements
        self._hostname = computer_conf['hostname']
        dev_type = screen_conf['device_type']
        if not dev_type:
            self.logger.error('Unknown device type !')
            return
        self._screen = {'graphic_buffer':
                                screen_conf['display']['graphic_buffer'],
                         'viewport': screen_conf['display']['viewport'],
                         'device_type': dev_type,
                         dev_type: screen_conf[dev_type],
                         'keep_focus': screen_conf['keep_focus']}

        self._log_file = os.path.join(system['log']['path'],
                                'BlenderVR_' + self.getName() + '.log')
        if system['log']['clear_previous']:
            self._log_to_clear = self._log_file
        else:
            self._log_to_clear = ''
        self._anchor = system['anchor']
        self._blender_player = {'executable':
                                        system['blenderplayer']['executable'],
                                'environments': {}}

        self._daemon = {'command': [],
                        'environments': {}}

        for name, value in system['daemon']['environments'].items():
            if system['daemon']['transmit']:
                self._blender_player['environments'][name] = str(value)
            self._daemon['environments'][name] = str(value)

        if hasattr(system['blenderplayer']['environments'], 'items'):
            for name, value in system['blenderplayer']['environments'].items():
                self._blender_player['environments'][name] = str(value)

        if hasattr(screen_conf['display']['environments'], 'items'):
            for name, value in screen_conf['display']['environments'].items():
                self._blender_player['environments'][name] = str(value)

        self._blender_player['options'] = screen_conf['display']['options']

        login = system['login']
        if login['remote_command']:
            self._daemon['command'] += shlex.split(login['remote_command'])
        self._daemon['command'].append(login['python'])
        self._daemon['command'].append(os.path.join(system['root'],
                                                    'utils', 'daemon.py'))
        self._daemon['command'].append(self._net_console)
        self._daemon['command'].append(self.getName())

        for index, argument in enumerate(self._daemon['command']):
            if ' ' in argument:
                self._daemon['command'][index] = '"' + argument + '"'

    def getHostname(self):
        return self._hostname

    def setHierarchy(self, informations):
        self._network = informations

    def is_master(self):
        return ('slaves' in self._network)

    def daemon_is_running(self):
        return (self._clients['daemon'] is not None)

    def _startDaemon(self):
        if self._process is None:
            command = copy.copy(self._daemon['command'])

            if self.profile.getValue(['debug', 'daemon']):  # Debug ?
                daemon_in = None
                daemon_out = None
                command.append('debug')
            else:
                daemon_in = open(os.devnull, 'r')
                daemon_out = open(os.devnull, 'w')

            try:
                if self.profile.getValue(['debug', 'executables']):
                    self.logger.error('Command to run daemon:',
                                      ' '.join(command))
                    self.logger.error('Its environment variables:',
                                      self._daemon['environments'])
                self._process = subprocess.Popen(command,
                         env=self._daemon['environments'],
                         stdin=daemon_in,
                         stdout=daemon_out,
                         stderr=daemon_out,
                         close_fds=('posix' in sys.builtin_module_names))
            except:
                self._cannot_start_daemon()
            else:
                self._check_daemon_timeout = self.getConsole().addTimeout(500,
                                                self._cannot_start_daemon)

    def _cannot_start_daemon(self):
        self._process = None
        self.logger.warning("Cannot start daemon for screen '" + self._name)

    def _stopDaemon(self):
        if self._process is not None:
            self._process.terminate()
            self._process.wait()
            self._process = None
            self.logger.info("Daemon for screen '" + self._name + "' stopped !")

    def setNetworkClient(self, origin, client, addr):
        if origin == 'daemon':
            if hasattr(self, '_check_daemon_timeout'):
                del(self._check_daemon_timeout)
            self.logger.info("Daemon for screen '" + self._name + "' started")
            if self._clients['daemon'] is not None:
                self.logger.error('Too many connexions of the daemon ...')
                return
            self._clients['daemon'] = client
            client.tag = self.getConsole().addListenTo(client.fileno(),
                                                    self._recv_from_daemon)
            for field in ['blender_player', 'log_to_clear']:
                client.send(field, getattr(self, '_' + field))
            self._send_loader_file()
            client.setCallback(self._message_from_daemon)
        elif origin == 'blender_player':
            if self._clients['blender_player'] is not None:
                self.logger.error('Too many connexionx of blenderplayer ...')
                return
            self._set_current_state('building')
            self._clients['blender_player'] = client

            client.tag = self.getConsole().addListenTo(client.fileno(),
                                            self._recv_from_blender_player)
            self._send_log_informations()
            self._send_log_to_file_information()
            for field in ['screen', 'complements', 'network', 'blender_file',
                                                        'processor_files']:
                client.send(field, getattr(self, '_' + field))
            client.send('base configuration ending')
            client.setCallback(self._message_from_blender_player)

    def _recv_from_daemon(self, *args):
        if self._clients['daemon'] is None:
            return False
        if not self._clients['daemon'].run():
            self._close_network_client(self._clients['daemon'])

    def _recv_from_blender_player(self, *args):
        if self._clients['blender_player'] is None:
            return False
        if not self._clients['blender_player'].run():
            self._close_network_client(self._clients['blender_player'])

    def _message_from_daemon(self, command, argument):
        if command in ['stdout', 'stderr']:
            self._write_to_window(command + '>' + argument)
        elif command in self.logger.getVerbosities():
            getattr(self.logger, command)(argument)
        elif command == 'configuration ok':
            self.logger.debug('Daemon successfully get its configuration')
        elif command == 'started':
            self._set_current_state('starting')
        elif command == 'stopped':
            self._set_current_state('stopped')
        elif command == 'log':
            self._write_to_window(argument)
        elif command == 'command':
            if self.profile.getValue(['debug', 'executables']):
                self.logger.error('Command to run blenderplayer:',
                                  ' '.join(argument['command']))
                self.logger.error('Its path:', argument['path'])
                self.logger.error('Its environment variables:',
                                  argument['environment'])
        elif command == 'forked':
            self._stopDaemon()
            self.logger.debug('Daemon forked !')
        else:
            self.logger.debug('Unkown message from daemon:', command, argument)
        return  True

    def _message_from_blender_player(self, command, argument):
        if command == 'log':
            self._write_to_window(argument)
        elif command == 'running':
            self._set_current_state('running')
        elif command == 'virtual_environment_to_console':
            self.getConsole().receivedFromVirtualEnvironment(argument)
        else:
            self.logger.debug('Unkown message from blenderplayer:',
                              command, argument)
        return  True

    def _close_network_client(self, client):
        if client is None:
            return
        self.getConsole().removeListenTo(client.tag)
        del(client.tag)
        client.close()
        if client == self._clients['daemon']:
            self._clients['daemon'] = None
            self._stopDaemon()
            if not self._stop:
                self._startDaemon()
        elif client == self._clients['blender_player']:
            self._clients['blender_player'] = None
            self.getConsole().updateStatus('Screen ' + self._name + ' stopped')
            self.getConsole()._update_status()

###########################################################
    #  Misc
    def adapt_simulation_files_to_screen(self, loader_file, blender_file,
                                                            processor_files):
        self._loader_file = loader_file.unstrip(self._anchor)
        self._blender_file = blender_file.unstrip(self._anchor)
        self._processor_files = []
        for processor_file in processor_files:
            self._processor_files.append(processor_file.unstrip(self._anchor))
        if self._blender_file is None:
            self._blender_file = ''
        if self._loader_file is None:
            self._loader_file = ''
        self._send_loader_file()

    def _send_loader_file(self):
        if (self._clients['daemon'] is not None) \
                                    and (self._loader_file is not None):
            self._clients['daemon'].send('loader_file', self._loader_file)

###########################################################
    #  BlenderPlayer commands

    def set_BlenderVR_state(self, state):
        if state != (self._state != 'stopped'):
            if self._clients['daemon']:
                self._clients['daemon'].send('state', state)

    def send_to_blender_player(self, command, argument=''):
        if self._clients['blender_player']:
            self._clients['blender_player'].send(command, argument)

    def ask_blender_player_to_quit(self):
        self.send_to_blender_player('quit')

    def get_blender_player_state(self):
        return self._state

    def _send_log_informations(self):
        self.send_to_blender_player('log_level',
            self.profile.getValue(['screens', self._name, 'log', 'level']))
        self.send_to_blender_player('log_to_controller',
            self.is_log_window_opened())

    def _send_log_to_file_information(self):
        if self.profile.getValue(['screens', self._name, 'log', 'file']):
            self.send_to_blender_player('log_file', self._log_file)
        else:
            self.send_to_blender_player('log_file', '')

    def _set_current_state(self, state):
        self._state = state
        self.getConsole().updateStatus('Screen ' + self._name + ' ' + state)
        self.getConsole()._update_status()
