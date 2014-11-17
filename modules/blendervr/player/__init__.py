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

"""@package blendervr
Main blenderVR module.

It has to be loaded by a python controller inside Blender File. Moreover, you should run blendervr.run() each frame (ie.: triggered by an Always Actuator). Thus, you should get the interactions
"""
import sys
import os
from . import exceptions
from .buffer import Buffer
from ..tools import protocol

from .. import is_virtual_environment
if not is_virtual_environment():
    sys.exit()

import bge

class Main:

    MESSAGE_PAUSE = b'p'
    MESSAGE_PROCESSOR = b'r'

    def __init__(self):
        """ Contstructor : load all necessary elements """
        self.run    = lambda *args : None
        self._scene = bge.logic.getCurrentScene()

        self._is_stereo = ('-s' in sys.argv)

        import builtins
        from ..tools import getModulePath
        builtins.blenderVR_root = os.path.dirname(os.path.dirname(os.path.dirname(getModulePath())))

        configuration = {}
        try:
            from ..tools import logger
            self._logger = logger.getLogger('blenderVR')

            # Define connexions until the controller is running ...
            console_logger = logger.Console()
            self._default_logger = self._logger.addLoginWindow(console_logger, True)
            self._logger.setLevel('debug')

            from .network import controller
            self._controller = controller.Controller(self)

        except:
            import traceback
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()
            bge.logic.endGame()
            sys.exit()            

        # Now, the logger is active !

        try:

            self._logger.removeHandler(self._default_logger)
            del(self._default_logger)

            configuration = self._controller.getConfiguration()

            self._screen_name = configuration['screen_name']
            del(configuration['screen_name'])

            self.logger.info('Current blender file: ' + configuration['blender_file'])

            # Load global dictionnary because we will use it later !
            bge.logic.loadGlobalDict()
            if 'blenderVR' not in bge.logic.globalDict:
                bge.logic.globalDict['blenderVR'] = {}

            self._paused = ''

            # Suspend the scene before getting the network because in standalone screen, resume can occure inside the constructor ...
            self._scene.suspend()

            # Configure the network connexions: deals with network
            from . import network
            self._connector, self._net_synchro = network.getNetworks(self, configuration['network'])

            del(configuration['network'])

            if 'complements' not in configuration:
                self.logger.fatal('Cannot find any "complements" information')

            if 'users' not in configuration['complements']:
                self.logger.fatal('Cannot find any "user" information')

            # Configure the users
            from . import user
            self._users = {}
            for userName, userInformation in configuration['complements']['users'].items():
                self._users[userName] = user.User(self, len(self._users), userInformation)
            del(configuration['complements']['users'])


            # Configure the screen: the elements that configure the projection for each window
            from . import screen
            self._screen = screen.getScreen(self, configuration['screen'])
            del(configuration['screen'])

            if self.isMaster():
                # Configure KEYBOARDANDMOUSE: module to get the interactions
                from . import keyboardAndMouse
                self._keyboardAndMouse = keyboardAndMouse.KeyboardAndMouse(self)

            from ..plugins import getPlugins
            self._plugins = getPlugins(self, self.logger)

            if 'plugins' in configuration['complements']:
                plugins_to_remove = []
                for plugin in self._plugins:
                    if plugin.getName() in configuration['complements']['plugins']:
                        try:
                            plugin.setConfiguration(configuration['complements']['plugins'][plugin.getName()])
                        except exceptions.PluginError as plugin_error:
                            if plugin_error.hasToClear():
                                plugins_to_remove.append(plugin)
                        except:
                            self.logger.log_traceback(False)
                for plugin_to_remove in plugins_to_remove:
                    self._plugins.remove(plugin_to_remove)
                del(plugins_to_remove)

            del(configuration['complements'])

            # Configure splash screen: the electocardiogram that is displayed when waiting for every connexions
            from . import splash
            self._splash = splash.Splash(self)

            # Configure the processor
            from ..processor import _getProcessor
            processor = _getProcessor(configuration['processor_files'], self.logger, True)
            del(configuration['processor_files'])
            try:
                self._processor = processor(self)
            except Exception as error:
                self.logger.error('Error inside the processor:')
                raise

            if hasattr(self, '_keyboardAndMouse') and not self._keyboardAndMouse.checkMethod(False):
                del(self._keyboardAndMouse)

            self._splash.setMessage("Waiting for all slaves !")
            self._splash.start()

            if hasattr(self, '_keyboardAndMouse'):
                self._keyboardAndMouse.start();

            self._plugin_hook('start')

            self._net_synchro.start()

            self.getProcessor().start()

            self.run = lambda *args : None
            self._scene.pre_render.append(self.wait_for_everybody)

        except exceptions.Common as error:
            self.logger.error(error)
        except IOError as error:
            self.logger.error(error)
        except:
            self.stopDueToError()

    def _plugin_hook(self, method, log_traceback = False):
        plugins_to_remove = []
        for plugin in self._plugins:
            if not hasattr(plugin, method):
                continue
            try:
                getattr(plugin, method)()
            except exceptions.PluginError as plugin_error:
                if plugin_error.hasToClear():
                    plugins_to_remove.append(plugin)
            except:
                if log_traceback:
                    self.logger.log_traceback(False)
        for plugin_to_remove in plugins_to_remove:
            self.logger.info('removing plugin:', plugin_to_remove.getName())
            self._plugins.remove(plugin_to_remove)

    def wait_for_everybody(self):
        try:
            self._controller.run()
            self._connector.wait_for_everybody()
            if self._connector.isReady():
                self._previous_pre_render = True
                self._scene.pre_render.remove(self.wait_for_everybody)
                if self.isMaster():
                    self.run = self._run_master
                else:
                    self.run = self._run_slave
                self._scene.pre_render.append(self._pre_render)
                self._startSimulation()
        except SystemExit:
            pass
        except:
            self.stopDueToError()

    def _run_master(self):
        # Ensure that run is call only once per frame ...
        if not self._previous_pre_render:
            return
        self._previous_pre_render = False
        try:
            self._processor.run()
            self._keyboardAndMouse.run()
            self._plugin_hook('run')
        except SystemExit:
            pass
        except:
            self.stopDueToError()
    
    def _run_slave(self):
        self._scene.suspend()

    def _run_default(self):
        try:
            self._controller.run()
        except SystemExit:
            pass
        except:
            self.stopDueToError()

    def _pre_render(self):
        try:
            self._controller.run()
            self._connector.run()
            self._screen.run()
            self._connector.endFrame()
            self._connector.barrier()
        except SystemExit:
            pass
        except:
            self.stopDueToError()
        self._previous_pre_render = True

    def getController(self):
        return self._controller

    def getScreenName(self):
        return self._screen_name

    def getUserByName(self, userName):
        """Given a user name, get its object, or raise an exception if the user does not exists"""
        if userName in self._users:
            return self._users[userName]
        raise exceptions.User('User "' + userName + '" not found')

    def getScreenUsers(self):
        return self._screen.getUsers()

    def getAllUsers(self):
        """Get the array of all the users"""
        return self._users

    def getSceneSynchronizer(self):
        """Get the main synchronizer module"""
        return self._net_synchro.getSceneSynchronizer()

    def addObjectToSynchronize(self, object, name):
        """Add an object to the synchronizer"""
        self._net_synchro.addObjectToSynchronize(object, name)

    def quit(self, reason):
        """Main quit method

        This method must be call instead of any other method to properly quit blenderVR.
        Otherwise, you may have problem of not closed socket next time you run blenderVR
        The reason is printed inside the log file of displayed on the console"""
        if hasattr(self, '_connector'):
            self._connector.quit(reason)

    def isMaster(self):
        """Are we the master rendering node ?

        Many treatment must be done only on the master rendering node.
        Some others must be done only on one node.
        In such case, you can check with this method"""
        return self._connector.isMaster()

    def getScale(self):
        """Get the scale between the virtual World and the Vehicule

        This method always return 1 for the moment: we have to improve the scale management !"""
        return 1

    def isPaused(self):
        if len(self._paused) > 0:
            return True
        return False

    def pause(self, title = ''):
        if not self.isMaster() or not isinstance(title, str):
            return
        self._pause(title)
        self._masterSendPause()

    def getPlugin(self, name):
        for plugin in self._plugins:
            if name == plugin.getName():
                if hasattr(plugin, 'virtual_environment'):
                    return plugin.virtual_environment
                return plugin
        return None

    def getProcessor(self):
        if hasattr(self, '_processor'):
            return self._processor
        return None

    def getNumberOfNodes(self):
        return self._connector.getNumberOfNodes()

    def stopDueToError(self):
        self.logger.log_traceback(True)
        self.logger.error('Due to previous error, we cannot continue to run blenderVR !')
        self._stopAll()

    @property
    def logger(self):
        return self._logger

    def _quitByNetwork(self, reason):
        """Internal quit: do not use"""
        self.logger.info('Quit: ' + reason)
        self._plugin_hook('quit')
        self._stopAll()
        bge.logic.saveGlobalDict()
        bge.logic.endGame()
        sys.exit()
        import time
        while True:
            time.sleep(1)

    def _stopAll(self):
        """Internal stop: do not use"""
        self.run = lambda *args : None
        if hasattr(self, '_pre_render') and self._pre_render in self._scene.pre_render:
            self._scene.pre_render.remove(self._pre_render)

    def _suspendResumeInternal(self):
        """Internal method to pause and resume the scene"""
        if self._connector.isReady() and not self.isPaused():
            # On doit demarrer la scene !
            if self.isMaster():
                self._scene.resume()
            self._splash.stop()
        else: # No network for the moment or pause !
            # On doit arreter la scene !
            self._scene.suspend()
            self._splash.start()
            if self._connector.isReady():
                self._splash.setMessage(self._paused)

    def _masterSendPause(self): 
        if not self.isMaster():
            return
        buffer = Buffer()
        buffer.command(self.MESSAGE_PAUSE)
        buffer.string(self._paused)
        self._connector.sendToSlave(buffer)

    def _sendToSlaves(self, command, argument = ''):
        buffer = Buffer()
        buffer.command(self.MESSAGE_PROCESSOR)
        buffer.string(protocol.composeMessage(command, argument))
        self._connector.sendToSlave(buffer)

    def _startSimulation(self):
        """Internal start of the simulation: do not use"""
        self._masterSendPause()
        self._suspendResumeInternal()
        self._controller.startSimulation()
        self.logger.info("The simulation is running ...")

    def _pause(self, title):
        self._paused = title
        self._suspendResumeInternal()

    def _messageFromMaster(self, buffer):
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.MESSAGE_PAUSE:
                self._pause(buffer.string())
            elif command == self.MESSAGE_PROCESSOR:
                command, argument = protocol.decomposeMessage(buffer.string())
                self._processor.receivedFromMaster(command, argument)
            
    def getVersion(self):
        from .. import version
        return version
