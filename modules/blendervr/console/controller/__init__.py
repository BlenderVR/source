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
from . import ui
from . import daemon
from . import logger
from ...tools import logger as tool_logger

class Controller():
    def __init__(self, profile_file, debug):
        self._debug = debug

        # Simulation informations
        self._blender_file       = None 
        self._loader_file        = None
        self._processor_files    = None

        self._anchor             = None
        self._previous_state     = None
        self._common_processors  = []

        self._uis                = []
        self._loggers            = []
        
        self._processor          = None

        self._controller_address = None

        from . import profile
        self._profile = profile.Profile(profile_file)

        self._logger = tool_logger.getLogger('blenderVR')

        from ...tools import getRootPath
        self._update_loader_script = os.path.join(getRootPath(), 'utils', 'update_loader.py')

        from . import logs
        self._logs = logs.Logs(self)

        if self._debug:
            # Define connexions until the controller is running ...
            tool_logger.Console(self._logger)
            self._logger.setLevel('debug')
            self.profile.setValue(['debug', 'daemon'], False)
            self.profile.setValue(['debug', 'executables'], False)

        from . import screens
        self._screens = screens.Screens(self)

        from ...plugins import getPlugins
        self._plugins = getPlugins(self, self._logger)

        from . import configuration
        self._configuration = configuration.Configuration(self)
        
    def start(self):
        from . import listener
        self._listener = listener.Listener(self)

        sys.stdout.write("***" + str(self.getPort()) + "***\n")
        sys.stdout.flush()
        from ... import version
        self.logger.info('blenderVR version:', version)
        self.configuration()
        if self._debug:
            self._logs.display()

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

    def quit(self):
        pass

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

        self._controller_address = configuration['console']['controller'] + ':' + str(self.getPort())
        self._screens.setConfiguration(configuration['screens'])
        del(configuration['screens'])

        self.runAction('start', 'daemon')
        self.update_user_files()

    def getCommonConfiguration(self):
        return None

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
                    self.logger.debug(self.logger.EXCEPTION)
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
    def logger(self):
        return self._logger

    @property
    def plugins(self):
        return self._plugins

    def runAction(self, action, element):
        self._screens.runAction(action, element)
