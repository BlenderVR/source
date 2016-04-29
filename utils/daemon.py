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

"""\
Daemon
******

This script runs in the clients rendering nodes and is responsible for spawning the
Blender Player with correct parameters, and sending feedback to the Console.

The daemon is started with command-line arguments. 
**First argument** is the network address ``host:port`` reference to contact the console.
**Second argument** is the *name* of the screen managed by that daemon.
An optional **third argument** can be ``debug`` to request activation of debugging
code in the daemon.


Messages
========


Management
----------

When started the daemon connect to the Console via its contact reference given on
command line arguments. Its first sent message is an  identification of itself with 
a command ``daemon`` giving the screen name as argument::

  daemon:"name"

If the daemon is the result of a fork, it send back to the Console a ``forked`` message
without parameter::

  forked:""

To stop the daemon, just send it a ``kill daemon`` message without parameter::

  kill daemon:""


Playing
-------

The daemon can receive a ``blender_player`` command specifying in arguments 
the parameters needed to start the blenderplayer process::

  blender_player:{'executable': "path to blenderplayer binary",
                  'option': "options to pass to executable"
                  'environments': { 'ENVIRONMENT_NAMES': 'ENVIRONMENT_VALUES' } }

If some log file has to be cleared before running the player, then the
daemon can receive a message with ``log_to_clear`` command specifying this 
file as argument::

  log_to_clear:"path to log file to remove"

Once the player context has been specified, you can indicate what file
must be played using command loader_file::

  loader_file:"file name of path to file"

To start the player, the daemon receive a ``state`` command with a bool arguments::

  state:True

To stop the player, Console can send a simple ``state`` command with a bool arguments::

    state:False

Once having a running player, the daemon send back a ``started`` command indication to the
Console, without argument::

  started:""

To explicitly stop the player, the daemon can receive a ``kill`` command, without
argument::

  kill:""

When the blender player has been started, the daemon send back a ``started`` command
without argument to the Console::

  started:""

When the blender player has been stopped, the daemon send back a ``stopped`` command
without argument to the Console::

  stopped:""


Information / Feedback
----------------------

Before starting the player, the daemon send back a ``command`` command
to the Console, specifying what local command and with what parameters will be
started::

  command:{'command': "command to start via subprocess",
           'environment': { 'ENVIRONMENT_NAMES': 'ENVIRONMENT_VALUES' },
           'path': "path to played file directory" }

In case of error, the daemon send back an ``stderr`` command with some informational
string as argument to the Console. 
It also send back this way any informations printed on the daemon's stderr stream::

  stderr:"error informations / printed informations"

In the same spirit, the daemon send back to the Console ``stdout`` commands with
string as argument for any printed line on daemon's stdout stream::

  stdout:"printed informations"

"""

# Inspired from daemonize module https://pypi.python.org/pypi/daemonize/
# But usable on Linux, Windows, MasOS… cannot use daemonize as is.

import sys
import threading
import socket
import tempfile
import io
import os
import subprocess
import threading


#: debug argument present as third parameter of daemon process on command line.
debug = False

#: Indicate that we have been double-forked to be a Unix daemon.
forked = False


class Daemon:
    """\
    Background management of the Blender Player and related stuff.


    """
    def __init__(self, BlenderVR_modules):
        self._BlenderVR_modules = BlenderVR_modules

        self._controller = sys.argv[1]
        self._screen_name = sys.argv[2].strip("'\"")

        self._process_in = subprocess.PIPE
        self._process_out = subprocess.PIPE

        import blendervr.tools.connector
        self._client = blendervr.tools.connector.Client(self._controller,
                                                'daemon', self._screen_name)
        self._client.setCallback(self.processCommand)
        self._client.setWait(True)

        #TODO: use os.name to identify Unixes (Linux, MacOS...) vs Windows
        # Registered: 'posix', 'nt', 'ce', 'java'.
        if ('posix' in sys.builtin_module_names):
            import signal
            signal.signal(signal.SIGTERM, self._exit)
        # else:
        #     try:
        #         import win32api
        #         win32api.SetConsoleCtrlHandler(self._exit, True)
        #     except ImportError:
        #         version = '.'.join(map(str, sys.version_info[:2]))
        #         raise Exception('pywin32 not installed for Python ' + version)

        if forked:  # Global set in module main() code.
            self._client.send_command('forked')

        self._loader_file = None
        self._loader_path = None
        self._process = None

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
            self._client.send_command('log', message.rstrip(' \n\r'))

    def __del__(self):
        self._stop_blender_player()

    def main(self):
        """Start the Daemon, quits any instance of BlenderPlayer running.
        """
        try:
            if not self._client.run():
                self._stop_blender_player()
        except socket.error:
            self._stop_blender_player()
        except SystemExit:
            self._stop_blender_player()
        except:
            if debug:
                import traceback
                traceback.print_exc()
            self._stop_blender_player()

    def processCommand(self, command, argument):
        """Run the received commands

        :param command: Command to execute in the client machine
        :type command: str
        :param argument: Value depends on the command
        :type argument: any jsonifiable content
        """
        BlenderVR_modules = self._BlenderVR_modules
        if command == 'blender_player':
            self._executable = argument['executable']
            self._executable_options = argument['options']
            self._environment = argument['environments']
            if 'PYTHONPATH' in self._environment:
                if BlenderVR_modules not in self._environment['PYTHONPATH']:
                    self._environment['PYTHONPATH'] = BlenderVR_modules \
                            + os.pathsep + self._environment['PYTHONPATH']
            else:
                self._environment['PYTHONPATH'] = BlenderVR_modules
        elif command == 'log_to_clear':
            self._log_to_clear = argument
        elif command == 'state':
            if argument:
                try:
                    import compileall
                    compileall.compile_dir("/".join((BlenderVR_modules,
                                                'blendervr')), quiet=True)
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
            self._exit()

    def _stop_blender_player(self):
        if self._process is not None:
            # Gently ask to stop !
            self._process.terminate()
            import time
            # Wait half a second
            time.sleep(0.5)
            if self._process:
                if self._process.poll() is None:
                    # If it does not want to stop, then, kill it !
                    self._process.kill()
                self._process.wait()
            self._process = None
            try:
                self._client.send_command('stopped')
            except:
                pass

    def _start_blender_player(self):
        if self._loader_file:
            if self._log_to_clear and os.path.isfile(self._log_to_clear):
                os.remove(self._log_to_clear)
            command = [self._executable]
            if self._executable_options:
                command += self._executable_options.split()
            command += [self._loader_file, '-', self._controller,
                        self._screen_name]

            for index, argument in enumerate(command):
                if ' ' in argument:
                    command[index] = '"' + argument + '"'

            try:
                self._client.send_command('command', {'command': command,
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
                self._client.send_command('stderr', 'Cannot start blenderplayer: '
                                                    + str(error))
            threading.Thread(target=Daemon._stream_waiter,
                                        args=(self, 'stdout')).start()
            threading.Thread(target=Daemon._stream_waiter,
                                        args=(self, 'stderr')).start()
            self._client.send_command('started')

    def _exit(self, *args):
        self._stop_blender_player()
        sys.exit()

    def _stream_waiter(self, stream_name):
        stream = getattr(self._process, stream_name)
        while True:
            lines = stream.readline()
            if not lines:   # Break on end of stream (closed).
                break
            lines = lines.rstrip(' \r\n')
            for line in lines.split('\n'):
                self._client.send_command(stream_name, line)
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

        # Close inherited file descriptors.
        import resource
        for fd in range(resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
            try:
                os.close(fd)
            except OSError:
                pass

        # Redirect stdin/stdout/stderr to /dev/null stream.
        # Note: updated with daemonize patch commited on 6 May 2014
        devnull_fd = os.open(devnull, os.O_RDWR)
        os.dup2(devnull_fd, 0)
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
        # Note: sys.stdout and sys.stderr are redirected by daemon to the
        # Console via TCP communications.

    # Find the installation root, and make blender package available.
    BlenderVR_root = os.path.dirname(os.path.dirname(__file__))
    BlenderVR_modules = "/".join((BlenderVR_root, 'modules'))
    sys.path.append(BlenderVR_modules)

    Daemon(BlenderVR_modules).main()


if __name__ == "__main__":
    main()
