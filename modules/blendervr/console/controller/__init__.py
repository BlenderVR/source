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
import sys
import subprocess
from . import ui
from . import logger
from .screen import player
from .screen import daemon
from .. import Console
from ...tools import logger as tools_logger

class Controller(Console):
    def __init__(self, profile_file, min_log_level, log_in_file, log_on_console):
        Console.__init__(self, min_log_level, log_in_file)

        # Simulation informations
        self._blender_file       = None 
        self._loader_file        = None
        self._processor_files    = None
        self._screenSets         = []

        self._anchor             = None
        self._previous_state     = None
        self._common_processors  = []

        self._uis                = []
        self._loggers            = []
        
        self._processor          = None

        self._controller_address = None

        from . import profile
        self._profile = profile.Profile(profile_file)

        from ...tools import getRootPath
        self._updater_script = os.path.join(getRootPath(), 'utils', 'updater.py')
        self._updater        = None

        self._blender_logger = tools_logger.getLogger('blender')
        self._blender_logger.setLevel(min_log_level)
        
        from .log_history import Log_History
        self._logs = Log_History(self)

        self._log_formatter = tools_logger.Formatter(self.addLogMessage)
        self.logger.addHandler(self._log_formatter)
        self._blender_logger.addHandler(self._log_formatter)

        if log_on_console:
            from ..logger.printer import Printer
            self._printer = Printer(self)
        
        from . import screens
        self._screens = screens.Screens(self)

        from ...plugins import getPlugins
        self._plugins = getPlugins(self, self._logger)

        from . import configuration
        self._configuration = configuration.Configuration(self)

        if os.name == "nt":
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(self.kill, True)
            except ImportError:
                version = '.'.join(map(str, sys.version_info[:2]))
                raise Exception('pywin32 not installed for Python ' + version)
        else:
            import signal
            for signal_name in ['SIGTERM', 'SIGQUIT']:
                try:
                    signum = getattr(signal, signal_name)
                    signal.signal(signum, self.kill)
                except:
                    self.logger.info('Invalid signal:', signal_name, ': ', signum)

    def _use_updater(self, blender_file = None):
        if blender_file:
            command = [sys.executable, self._updater_script, '--', blender_file]
        else:
            if not os.path.isfile(self._loader_file):
                self.logger.debug('Creating loader')
            else:
                self.logger.debug('Updating loader')
            command = [self._blender_exe, '-b', '-P', self._updater_script, '--', self._blender_file] + self._processor_files
        if self.profile.getValue(['debug', 'executables']):
            self.logger.debug('Command to get the updater:', ' '.join(command))

        for index, argument in enumerate(command):
            if ' ' in argument:
                command[index] = '"' + argument + '"'

        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        loader_name = None
        
        import json

        for line in process.stdout:
            line = line.decode('UTF-8').rstrip()
            if not line:
                continue
            try:
                messages = json.loads(line)
            except:
                self._blender_logger.info(line)
                continue
            for context, message in messages.items():
                if context == 'logger':
                    self.addLogMessage(message)
                    continue
                if context == 'loader':
                    loader_name = message
        for line in process.stderr:
            line = line.decode('UTF-8').rstrip()
            if not line:
                continue
            self._blender_logger.warn(line)
        return loader_name

    def __del__(self):
        self.kill()

    def start(self):
        from . import listener
        self._listener = listener.Listener(self)

        sys.stdout.write("***" + str(self.getPort()) + "***\n")
        sys.stdout.flush()
        self.profile.setValue('port', self.getPort())
        from ... import version
        self.logger.info('blenderVR version:', version)

        if hasattr(self, '_printer'): # log on console !
            for msg in self._logs.getAllMessages():
                self._printer.print(msg)
            self._logs.addCallback(self._printer.print)

        self.configuration()

    def getPort(self):
        return self._listener.getPort()

    def getControllerAddress(self):
        return self._controller_address
    
    def main(self):
        while True:
            try:
                self._listener.select()
            except (KeyboardInterrupt, SystemExit):
                break

    def kill(self, *argv):
        if self.profile.getValue('port'):
            self.profile.setValue('port', None)
            self.runAction('kill', 'all')
            del(self._screens)
            for ui in self._uis:
                ui.kill()
                del(ui)
            del(self._uis)
            for logger in self._loggers:
                logger.kill()
                del(logger)
            del(self._loggers)
            # We must destroy the listener at the end as it is the first created and that it will destroy the master socket
            del(self._listener)

    def _create_client(self, client):
        type = client.getType()
        if type == 'UI':
            userInterface = ui.UI(self, client)
            self._uis.append(userInterface)
            return userInterface
        if type == 'daemon':
            daemonClient = daemon.Daemon(self, client)
            self._screens.appendClient(daemonClient)
            return daemonClient
        if type == 'logger':
            loggerClient = logger.Logger(self, client)
            self._loggers.append(loggerClient)
            return loggerClient
        if type == 'player':
            playerClient = player.Player(self, client)
            self._screens.appendClient(playerClient)
            return playerClient
        self.logger.error('Cannot understand client type :', type)

    def _delete_client(self, client):
        if client in self._uis:
            self._uis.remove(client)
            return

    def configuration(self):
        """
        Called whenever the configuration file changed (file modified or user choose another file) 
        """
        self._configuration.load()

    def screenSets(self, screenSets):
        """
        Called by the configuration file loader
        """
        self._screenSets = screenSets
        self.screenSet()

    def getScreenSets(self):
        return self._screenSets
            
    def screenSet(self):
        self.updateConfiguration()

    def updateConfiguration(self):
        configuration = self._configuration.getConfiguration()
        if not configuration:
            return

        self._blender_exe = configuration['console']['blender_exe']
        
        self._controller_address = configuration['console']['controller'] + ':' + str(self.getPort())
        self._screens.setConfiguration(configuration['screens'], configuration['complements'], configuration['console']['port'])
        del(configuration['screens'])

        self.runAction('start', 'daemon')
        self.update_user_files()

    def getCommonConfiguration(self):
        return None

    def update_user_files(self, force = False):
        blender_file = self.profile.getValue(['simulation', 'blender', 'file'])

        processor_files = [self.profile.getValue(['simulation', 'processor', 'file'])] + self._common_processors
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
                    self.logger.debug(self.logger.EXCEPTION)
                self._processor = None
                processor_files = []

        loader_file = None
        if self._processor and self._processor.useLoader():
            loader_file = self._use_updater(blender_file)
        if not loader_file:
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

    def updateLoader(self):
        if self._processor and self._processor.useLoader():
            update = not os.path.isfile(self._loader_file)
            if not update:
                loader_time = os.path.getctime(self._loader_file)
                for processor_file in [self._blender_file] + self._processor_files:
                    if os.path.getctime(processor_file) > loader_time:
                        update = True
                        break
            if update:
                self._use_updater()

    def addTimeout(self, time, callback):
        """
        Add a timeout for a method. Return an index that can be use to del the timeout.

        :param time: the time for the timeout in seconds
        :type time: integer
        :param callback: the method to call when the timemout occurs
        :type time: method
        :rtype: timeout index
        """
        return self._listener.addTimeout(time, callback)
        
    def delTimeout(self, index):
        """
        Del a timeout.

        :param index: the index given by addTimeout or the method to remove
        :type time: index or method
        :rtype: boolean
        """
        return self._listener.delTimeout(index)

    @property
    def profile(self):
        return self._profile

    @property
    def plugins(self):
        return self._plugins

    def runAction(self, action, element):
        self._screens.runAction(action, element)

    def addLogMessage(self, message):
        self._logs.addMessage(message)

    def getStatus(self):
        return self._screens.getStatus()
