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

'''
    This class is supposed to replace the qt class in the console package. Its responsibility is to parse the arguments
    sent by the terminal class, process the requests, and do the commands.
'''

import sys
import os
import argparse
import _thread


#TODO Linking capabilities (Should be pretty easy but i don't think it would be very useful)

class Argument_handler():

    def __init__(self, parent=None):

        #Start the parser
        self._parser = argparse.ArgumentParser()

        self._parser.add_argument("--print-configuration", "-pc", dest = "print_conf", help = "Print current configuration", action='store_true', default = False)
        self._parser.add_argument("--set-configuration-file", "-sc", dest = "new_configuration_file", help = "Set new configuration file", default = None)
        self._parser.add_argument("--set-blender-file", "-sb", dest = "new_blender_file", help = "Set new blender file", default = None)
        self._parser.add_argument("--set-processor-file", "-sp", dest = "new_processor_file", help = "Set new processor file", default = None)
        self._parser.add_argument("--reload-daemon", "-r-d", dest = "daemon", help = "Reload the Daemon", action = "store_true", default = False)
        self._parser.add_argument("--reload-processor", "-r-p", dest = "process", help = "Reload the processor", action = "store_true", default = False)

        #screens. to use write screens -d or screens -c new_screen
        sub = self._parser.add_subparsers(dest='mode')
        parser = sub.add_parser('screens')
        parser.add_argument("-d", dest = "display_screens", help = "Display all the available screens with their corresponding indexes", action = "store_true", default = False)
        parser.add_argument("-c", dest = "screen_name", help = "Change screen using their name or their index", default = None)

        #log. to use write log -d to display all the log level available or log -c new_log
        parser = sub.add_parser('log')
        parser.add_argument("-d", dest = "display_log", help = "Display all the available log levels with their corresponding indexes", action = "store_true", default = False)
        parser.add_argument("-c", dest = "new_log", help = "Set log level of the logger: <1|critical, 2|error, 3|warning, 4|info, 5|debug>", default = None)
        parser.add_argument("-log-in-file", '-lf', dest = "file", help = "Log all messages to given file.", default = None)
        parser.add_argument("-stop-console", '-sm', '-silent-mode', dest = "silent_mode", help = "Use BlenderVR in silent mode, no log output in the console", action = 'store_true', default = False)
        parser.add_argument("-start-output-console", '-ssm', '-stop-silent-mode', dest = "stop_silent_mode", help = "Turn off silent mode, output will be redirected to the console", action = 'store_true', default = False)

        parser = sub.add_parser('simulation')
        parser.add_argument("--start", "-start", dest = "start", help = "Start Simulation", action = "store_true", default = False)
        parser.add_argument("--stop", "-stop", dest = "stop", help = "Stop Simulation", action = "store_true", default = False)

    #will run everytime a new argument is passed
    def main(self, argument):

        #stop argparse from terminating the program
        try:
            environment = self._parser.parse_args(argument)
        except SystemExit:
            environment = None

        #do the commands
        if environment is not None:
            if environment.print_conf:
                self.print_configuration()

            if environment.new_configuration_file:
                self.change_config_file(environment.new_configuration_file)

            if environment.new_blender_file:
                self.change_blender_file(environment.new_blender_file)

            if environment.new_processor_file:
                self.change_processor_file(environment.new_processor_file)

            if environment.daemon:
                self.restart_daemon()

            if environment.process:
                self.restart_processor()

            if environment.mode is not None:

                if environment.mode == 'screens':
                    if environment.display_screens:
                        self.display_screen()

                    if environment.screen_name:
                        self.change_screen(environment.screen_name)

                elif environment.mode == 'log' :
                    if environment.display_log:
                        self.display_log()

                    if environment.new_log:
                        self.set_log_level(environment.new_log)

                    if environment.file:
                        self.log_in_file(environment.file)

                    if environment.silent_mode:
                        self.silent_mode()

                    if environment.stop_silent_mode:
                        self.stop_silent_mode()

                if environment.mode == 'simulation':
                    if environment.start:
                        self.start_simulation()

                    if environment.stop:
                        self.stop_simulation()



    #Log in File
    def log_in_file(self, file):
        try:
            import logging
            file_handling = logging.FileHandler(file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:    %(message)s')
            file_handling.setFormatter(formatter)
            self.logger.addHandler(file_handling)

            self.logger.info("File succesfully linked to the logger")

        except Exception as e:
            print("File not linked. Error message: " + str(e))

    #print current configuration
    def print_configuration(self):

        import pprint
        print("\033[0;32m Current Configuration: \033[0m")
        pprint.pprint(self._configuration)


    #set log level
    def set_log_level(self, level):
        if level.lower() == '1' or level.lower() == 'critical':
            self.logger.setLevel('critical')
            self.logger.critical("Log Level succesfully changed to CRITICAL")
            self.log_level = 'critical'

        elif level.lower() == '2' or level.lower() == 'error':
            self.logger.setLevel('error')
            self.logger.critical("Log Level succesfully changed to ERROR")
            self.log_level = 'error'

        elif level.lower() == '3' or level.lower() == 'warning':
            self.logger.setLevel('warning')
            self.logger.critical("Log Level succesfully changed to WARNING")
            self.log_level = 'warning'

        elif level.lower() == '4' or level.lower() == 'info':
            self.logger.setLevel('info')
            self.logger.critical("Log Level succesfully changed to INFO")
            self.log_level = 'info'

        elif level.lower() == '5' or level.lower() == 'debug':
            self.logger.setLevel('debug')
            self.logger.critical("Log Level succesfully changed to DEBUG")
            self.log_level = 'debug'
        else:
            print("Option not valid. Valid options :")
            self.display_log()

        self.profile.setValue(['terminal', 'log_level'], self.log_level)

    #display all available log levels
    def display_log(self):
        list_level = ['critical', 'error', 'warning', 'info', 'debug']

        for level in list_level:
            print("Index: " + str((list_level.index(level) + 1)) + " Level: " + level)

    #change configuration file
    def change_config_file(self, config_file, screen = None, load=True):
        #check if file exists and if it has an .xml extension
        if os.path.isfile(config_file) and config_file.endswith('.xml'):
            #get the full path of the config file
            config_path = os.path.realpath(config_file)
            config_path = config_path.replace('\\','\\\\')
            self.profile.setValue(['config', 'file'], config_path)
            self.logger.info("Configuration file: " + config_path + " successfully added to the profile file")

            if screen is not None:
                self.profile.setValue(['screen', 'set'], screen)
            try:
                self.load_configuration_file()
                self.logger.info("Configuration file: " + config_path + " successfully loaded")
                return True

            except Exception as e:
                print(e)
                print("Could not load configuration file")
                return False

        else:
            print("The configuration file: " + config_file + " isn't an .xml file or doesn't exist.")
            return False

    def change_blender_file(self, blender_file):
        #check if file exists and if it is a .blend extension
        if os.path.isfile(blender_file) and blender_file.endswith('.blend'):

            #get the full path of the blend file
            blender_path = os.path.realpath(blender_file)
            self.profile.setValue(['files', 'blender'], blender_path)
            self.logger.info("Blender file: " + blender_path + " successfully loaded")
        else:
            print("The blender file: " + blender_file + " isn't an .blend file or doesn't exist.")
            return False
        self.update_user_files()
        return True

    def change_processor_file(self, processor_file):
        #check if file exists and if it is a .blend extension
        if os.path.isfile(processor_file) and processor_file.endswith('.py'):

            #get the full path of the config file
            processor_path = os.path.realpath(processor_file)           
            self.profile.setValue(['files', 'processor'], processor_path)
            self.logger.info("Processor file: " + processor_path + " successfully loaded")

        else:
            print("The processor file: " + processor_file + " isn't an .py file or doesn't exist.")
            return False

        self.update_user_files()
        return True

    def display_screen(self):
        i = 1
        for screen in self._possibleScreenSets:
            print("Index: " + str(i) + " Screen: " + screen)
            i = i + 1


    def change_screen(self, screen, load=True):
        #check if the string sent by the user is an integer
        index = None
        try:
            index = int(screen)
        except:
            pass

        #if the input is a number use it to select the screen
        if(index):
            try:
                self.profile.setValue(['screen', 'set'], self._possibleScreenSets[index - 1])
                if load:
                    self.set_screen_set()
                self.logger.info("Screen " + self._possibleScreenSets[index-1] + " succesfully loaded..." )
                return True

            except:
                print("Index not valid... ")
                print("Valid Options:   ")
                self.display_screen()
                return False

        #else, if the string is referring to the name of a screen
        elif screen in self._possibleScreenSets:
            self.profile.setValue(['screen', 'set'], self._possibleScreenSets[self._possibleScreenSets.index(screen)])
            if load:
                self.set_screen_set()
            self.logger.info("Screen " + self._possibleScreenSets[self._possibleScreenSets.index(screen)] + " succesfully loaded..." )
            return True
        else:
            print("Option not valid.... ")
            print("Valid Options:   ")
            self.display_screen()
            return False

    #start silent mode
    def silent_mode(self):
        import logging

        if self._silent_mode:
            print("Silent mode already activated...")
        else:
            print("Starting silent mode. Only blender output will be displayed. You might want to redirect the output to a file with log -lf FILE")
            for handler in self._logger.handlers:
                if(isinstance(handler,logging.StreamHandler)):
                    self._logger.removeHandler(handler)

            self.profile.setValue(['terminal', 'silent_mode'], True)
            self._silent_mode = True

    #stop silent mode
    def stop_silent_mode(self):
        import logging

        if self._silent_mode:
            mprint = CustomPrint()

            #create stdout handler for the logger
            handler = logging.StreamHandler(mprint)
            #create formatter for the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:    %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)
            self.logger.setLevel(self.log_level)
            self.logger.info("Console logger activated")

            self.profile.setValue(['terminal', 'silent_mode'], False)
            self._silent_mode = False
        else:
            print("Console logger is already activated...")


    ''' Variant of the addListenTo in the console.qt package. Instead of using a QTSocketHandler, which requires a QThread
    we are using a custom socket handler class. it uses the select method which is supported by most OS nowadays.'''
    def addListenTo(self, socket, callback):
        from . import sockethandler
        handler = sockethandler.SocketThread(socket, callback)
        handler.start()
        return handler

    def removeListenTo(self, tag):
        del tag

    #Change the screen set
    def cb_set_screen_set(self):
        all_screen_sets = self._possibleScreenSets
        current = all_screen_sets[0]
        self.profile.setValue(['screen', 'set'], current)
        self.set_screen_set()

    ''' Variant of the addTimeout in the console.qt package. Instead of using a QTimer, which requires a QThread
    we are using the default timer of python.'''
    def addTimeout(self, time, callback):
        from . import timer
        timer = timer.Timerd(time/1000, callback)
        timer.start()
        return timer

    def restart_daemon(self):
        for name, obj in self._screens._screens.items():
            obj.restartDaemon()

        self.logger.info("All daemons succesfully restarted.....")

    def restart_processor(self):
        self.update_user_files()

    def updateStatus(self, message, state=None):
        self.state = message


''' Here is where I tried to fix the problem with the input cursor after some printing from a different thread, The write
function will be called everytime someone calls self.logger.whatever(text) '''
class CustomPrint():
    def __init__(self):
        self.old_stdout=sys.stdout

    def write(self, text):
        if len(text) == 0: return
        self.old_stdout.write(text)
