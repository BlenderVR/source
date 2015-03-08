# -*- coding: utf-8 -*-
# file: utils/daemon.py

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

"""
Daemon
******

This script runs in the clients and is responsible for spawning the
Blender Player.
"""

import sys
import threading
import socket
import tempfile
import io
import os
import subprocess
import threading

debug = False
forked = False


class Daemon:
    """Background management of the Blender Player and related stuff.
    """
    def __init__(self, blenderVR_modules):
        self._blenderVR_modules = blenderVR_modules

        self._loader_file = None
        self._loader_path = None
        self._process = None

        from blendervr.tools import logger
        self._logger = logger.getLogger('daemon')
        
        self._controller_name = sys.argv[1]
        self._screen_name = sys.argv[2].strip("'\"")

        self._process_in = subprocess.PIPE
        self._process_out = subprocess.PIPE

        import blendervr.tools.controller
        try:
            self._controller_connexion = blendervr.tools.controller.Controller(self._controller_name, 'daemon', self._screen_name)
        except:
            console_logger = logger.Console(self._logger)
            self._logger.warning(self._logger.EXCEPTION)
        if not hasattr(self, '_controller_connexion'):
            return

        #TODO: use os.name to identify Unixes (Linux, MacOS...) vs Windows
        # Registered: 'posix', 'nt', 'ce', 'java'.
        if ('posix' in sys.builtin_module_names):
            import signal
            signal.signal(signal.SIGTERM, self._exit)
        else:
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(self._exit, True)
            except ImportError:
                version = '.'.join(map(str, sys.version_info[:2]))
                raise Exception('pywin32 not installed for Python ' + version)

        if forked:
            self._controller_connexion.send('forked')

        logger.Network(self._logger, self._controller_connexion, 'logger')

    def write(self, *messages):
        """Send message to the client

        :param messages: all the messages to send to the client (i.e., console
            commands)
        :type messages: list
        """
        elements = []
        for message in messages:
            elements.append(str(message))
        for message in (' '.join(elements)).split('\n'):
            self._controller_connexion.send('log', message.rstrip(' \n\r'))

    def __del__(self):
        self.quit()

    def _exit(self, *args):
        sys.exit()
        
    def quit(self, *args):
        if hasattr(self, '_controller_connexion'):
            self._controller_connexion.close()
            self._controller_connexion = None
        self._stop_blender_player()

    def main(self):
        if not hasattr(self, '_controller_connexion'):
            return
        """Start the Daemon, quits any instance of BlenderPlayer running.
        """
        try:
            while True:
                msg = self._controller_connexion.receive()
                if msg:
                    self.processCommand(*msg)
                else:
                    sys.exit()
        except (socket.error, SystemExit, KeyboardInterrupt):
            pass
        except:
            if debug:
                import traceback
                traceback.print_exc()

    def processCommand(self, command, argument):
        """Run the received commands

        :param command: Command to execute in the client machine
        :type command: str
        :param argument: Value depends on the command
        """
        blenderVR_modules = self._blenderVR_modules
        if command == 'blender_player':
            self._executable = argument['executable']
            self._executable_options = argument['options']
            self._environment = argument['environments']
            if 'PYTHONPATH' in self._environment:
                if blenderVR_modules not in self._environment['PYTHONPATH']:
                    self._environment['PYTHONPATH'] = blenderVR_modules \
                            + os.pathsep + self._environment['PYTHONPATH']
            else:
                self._environment['PYTHONPATH'] = blenderVR_modules
        elif command == 'log_to_clear':
            self._log_to_clear = argument
        elif command == 'state':
            if argument:
                try:
                    import compileall
                    compileall.compile_dir(os.path.join(blenderVR_modules,
                                                'blendervr'), quiet=True)
                except:
                    pass
                self._start_blender_player()
            else:
                self._stop_blender_player()
        elif command == 'loader_file':
            dirname = os.path.dirname(argument)
            if os.path.isdir(dirname):
                self._loader_file = os.path.basename(argument)
                self._loader_path = dirname
            else:
                self._loader_file = argument
                self._loader_path = None
        elif command == 'kill':
            self._stop_blender_player()
        elif command == 'kill daemon':
            sys.exit()

    def _stop_blender_player(self):
        if self._process is not None:
            from blendervr.tools import gentlyAskStopProcess
            gentlyAskStopProcess(self._process)
            self._process = None
            try:
                self._controller_connexion.send('stopped')
            except:
                pass

    def _start_blender_player(self):
        if self._loader_file:
            if self._log_to_clear and os.path.isfile(self._log_to_clear):
                os.remove(self._log_to_clear)
            command = [self._executable]
            if self._executable_options:
                command += self._executable_options.split()
            command += [self._loader_file, '-', self._controller_name,
                        self._screen_name]

            for index, argument in enumerate(command):
                if ' ' in argument:
                    command[index] = '"' + argument + '"'

            try:
                self._controller_connexion.send('command', {'command': command,
                                              'environment': self._environment,
                                              'path': self._loader_path})
                self._process = subprocess.Popen(command,
                             env=self._environment,
                             stdin=self._process_in,
                             stdout=self._process_out,
                             stderr=self._process_out,
                             cwd=self._loader_path,
                             universal_newlines=True,
                             #TODO: use os.name == 'posix'
                             close_fds=('posix' in sys.builtin_module_names))
            except Exception as error:
                self._controller_connexion.send('stderr', 'Cannot start blenderplayer: '
                                                    + str(error))
            threading.Thread(target=Daemon._stream_waiter, args=(self, 'stdout')).start()
            threading.Thread(target=Daemon._stream_waiter, args=(self, 'stderr')).start()
            self._controller_connexion.send('started')

    def _stream_waiter(self, stream_name):
        stream = getattr(self._process, stream_name)
        while True:
            lines = stream.readline()
            if not lines:
                break
            lines = lines.rstrip(' \r\n')
            for line in lines.split('\n'):
                self._controller_connexion.send(stream_name, line)
        if stream_name == 'stdout':
            self._stop_blender_player()

def main():
    """Main function to start the daemon.

    Prepare execution (daemonize if necessary), then build a Daemon and
    call its main() method to manage background communications.
    """
    global debug
    global forked

    if len(sys.argv) > 3 and sys.argv[3] == 'debug':
        debug = True
    else:
        debug = False

    if not debug:
        try:
            # on Linux, we daemonize !
            process_id = os.fork()
            forked = True
        except:
            forked = False
    else:
        forked = False

    if forked:
        if process_id < 0:
            # Fork error.  Exit badly.
            sys.exit(1)
        elif process_id != 0:
            # This is the parent process.  Exit.
            sys.exit(0)

        process_id = os.setsid()
        if process_id == -1:
            # Uh oh, there was a problem.
            sys.exit(1)

        devnull = "/dev/null"
        if hasattr(os, "devnull"):
            # Python has set os.devnull on this system, use it instead
            # as it might be different than /dev/null.
            devnull = os.devnull

        import resource
        for fd in range(resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
            try:
                os.close(fd)
            except OSError:
                pass

        os.open(devnull, os.O_RDWR)
        #TODO: LPOINTAL: usage of duplicating (twice) stdin and bad dup() ?
        # Maybe second call should be os.dup(1).
        # And, what is done with values ? Maybe should use dup2() which
        # close the old file and to specify if the new is inheritable
        # or not (for dup(), its non-inheritable in Unix, inheritable on
        # windows.
        os.dup(0)
        os.dup(0)

    # Find the installation root, and make blender package available.
    blenderVR_root = os.path.dirname(os.path.dirname(__file__))
    blenderVR_modules = os.path.join(blenderVR_root, 'modules')
    sys.path.append(blenderVR_modules)

    daemon = Daemon(blenderVR_modules)
    daemon.main()
    daemon.quit()
    del(daemon)


if __name__ == "__main__":
    main()
