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

from . import base
import os
import copy
import subprocess
import sys
from . import daemon

class Screen(base.Base):
    def __init__(self, parent, name):
        base.Base.__init__(self, parent)
        self._name    = name
        self._process = None

        self._clients = {'daemon': None,
                         'blender_player': None}

    def __del__(self):
        self.kill()

    def kill(self):
        from ...tools import gentlyAskStopProcess
        gentlyAskStopProcess(self._process)
        self._process = None
        if self._clients['blender_player']:
            self._clients['blender_player'].kill()
            self._clients['blender_player'] = None
        if self._clients['daemon']:
            self._clients['daemon'].kill()
            self._clients['daemon'] = None

    def getName(self):
        return self._name

    def setConfiguration(self, configuration):
        screen_conf   = configuration['screen']
        computer_conf = configuration['computer']
        system        = computer_conf['system']

        self._hostname    = computer_conf['hostname']
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
                                'blenderVR_' + self.getName() + '.log')
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
        self._daemon['command'].append(os.path.join(system['root'], 'utils', 'daemon.py'))
        self._daemon['command'].append(self.controller.getControllerAddress())
        self._daemon['command'].append(self.getName())

        for index, argument in enumerate(self._daemon['command']):
            if ' ' in argument:
                self._daemon['command'][index] = '"' + argument + '"'

    def runAction(self, action, element):
        if action == 'kill':
            self.kill()
        elif element == 'daemon':
            if action == 'start':
                self._startDaemon()
        elif element == 'simulation':
            if action == 'start':
                print('START !')
            else:
                print('STOP !')

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
                    self.logger.debug('Command to run daemon:', ' '.join(command))
                    self.logger.debug('Its environment variables:', self._daemon['environments'])
                self._process = subprocess.Popen(command, env=self._daemon['environments'],
                                                 stdin=daemon_in, stdout=daemon_out, stderr=daemon_out,
                                                 close_fds=('posix' in sys.builtin_module_names))
            except:
                self._cannot_start_daemon()
            else:
                self._check_daemon_timeout = self.controller.addTimeout(5, self._cannot_start_daemon)

    def appendClient(self, client):
        if isinstance(client, daemon.Daemon):
            if hasattr(self, '_check_daemon_timeout'):
                self.controller.delTimeout(self._check_daemon_timeout)
                del(self._check_daemon_timeout)
            if self._clients['daemon'] is not None:
                self.logger.error('Too many connexions of the daemon ...')
                return
            self._clients['daemon'] = client
            self.logger.info("Daemon for screen '" + self._name + "' started")
            for field in ['blender_player', 'log_to_clear']:
                client.send(field, getattr(self, '_' + field))
            self._send_loader_file()

    def _cannot_start_daemon(self):
        self._process = None
        self.logger.warning("Cannot start daemon for screen '" + self._name)

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
