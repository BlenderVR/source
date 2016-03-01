Author = Michael Perez, Brown University Intern, CCV Department.

Manual
-----------------------------------------------
With this version of BlenderVR, you have four ways to render a blender application:
1) The classic GUI. Just call the program with no arguments. 
Example:
    $: ./blendervr

2) An on-the-fly rendering, meaning that you will write a command telling BlenderVR the files that you want for the render.
   Example:
    $: ./blendervr start -configuration CONFIG_PATH -screen SCREEN_NAME -processor PROCESSOR_PATH -blend BLENDER_FILE_PATH

   You can also use an additional property called -log to log all the output to a certain file.
   Example:
    $: ./blendervr start -configuration CONFIG_PATH -screen SCREEN_NAME -processor PROCESSOR_PATH -blend BLENDER_FILE_PATH -log LOG_FILE

3) An on-the-fly rendering with a predefined configuration file. This mode does the same thing as mode number 2, the difference
is that all the values are already predefined in a launch-configuration xml file. See an example under source/samples/profile_spider.xml
   Example:
    $: ./blendervr start-xml -start LAUNCH_XML_PATH

   You can also use an additional property called -log just like in mode number 2

4) The in-console mode, is the same as the GUI mode, without the GUI. you can change files, load files, restart the daemon,
log in file, start and stop simulation. It is a terminal application and requires user commands to work.
    To start the in-console mode use:
     $: ./blendervr --start-in-console


*********PARAMETERS******************

____________________________BlenderVR launching parameters______________________________________

-h: Help

--version : Prints the version of BlenderVR
  Example:
    $: ./blendervr --version
    Current version: 1.0

--BlenderVR-root: Change the BlenderVR root folder
  Example:
    $: ./blendervr --BlenderVR-root ~/blendervr_new/source

--display-console: Displays the current configuration of BlenderVR. 

--delete-console: Resets all the configuration of BlenderVR.

--start-in-console: Starts the in-console mode. 

****** start *****
This is the flag used to access the on-the-fly rendering without xml. 

___required fields___
-configuration: inputs the path of the configuration file
-screen: inputs the name of the screen for the render
-blend: inputs the path of the blender file to render
-processor: inputs the path of the processor file to render

___optional fields___
-log : inputs the path of a file (if the file doesn't exist, it will be created) that 
will be used to output all the log messages.

Example: 
  $: ./blendervr start -configuration CONFIG_PATH -screen SCREEN_NAME -processor PROCESSOR_PATH -blend BLENDER_FILE_PATH -log LOG_FILE

****** start-xml ******
This is the flag used to access the on-the-fly rendering with an xml file. 

___required fields___
-start: Path of the xml file for the application. 

___optional fields___
-log : inputs the path of a file (if the file doesn't exist, it will be created) that will be used to output all the log messages.
-screen : name of the screen that will be used for this render. If this isn't inputted, BlenderVR will use the default
that's especified in the configuration file.

Example:
  $: ./blendervr start-xml -start LAUNCH_XML_PATH -screen SCREEN_NAME -log LOG_FILE

____________________________BlenderVR in-console mode parameters______________________________________

-h: HELP
 
--print-configuration, -pc: Prints an overview of the current configuration file. 

--set-configuration-file, -sc: inputs the path of a configuration file and sets the new configuration file to the application.
Example:
  >> --set-configuration-file configurations/config.xml

--set-blender-file, sb: inputs the path of a blender file and sets the new blender file to the application.
  >> --set-blender-file blender_apps/game1.blend

--set-processor-file, -sp: inputs the path of a python file and sets the new python file as the processor.
  >> --set-blender-file blender_apps/game1.processor.py

--reload-daemon, -r-d: Relaods the daemon

--reload-processor, -r-p: Reloads the processor

****** screens ******
-d: display available screens
Example:
  >> screens -d

-c: Change the current screen. The input can be the name of the screen, or its index. call -d to see their indexes. 
Example:
  >> screens -c Console
or 
  >> screens -c 2

****** log ******
-d: display all the available log levels
Example:
  >> log -d

-c: change the current log level. The input can be the name of the level, or its index. call -d to see their indexes. 
  >> log -c Critical
or 
  >>log -c 1

-log-in-file, -lf: Log all messages to given file
Example:
  >> log -lf log.txt (The file will go to the current directory of the terminal)

-stop-console, -sm, -silent-mode: Use BlenderVR in silent mode, no log output in the console. 

-start-output-console, -ssm, -stop-silent-mode: Stop BlenderVR's silent mode.

****** simulation ******

--start, -start: Start simulation

--stop, -stop: Stop simulation

Changes
-----------------------------------------------

New Files:
-----------------------
source/samples:

    * profile_spider.xml: XML example of a launcher file for an application. Use this template to create launcher files for
    your blender applications.

********************
source/modules/terminal:

    *__init__.py : The same __init__ as the console package
    *base.py: The same base as the console package
    *profile.py: The same profile
    *screen.py: inherits the base.Base and the console.logic.screen.Logic classes
    *screens.py: __init__, start, and quit, for the console.logic.screens.Logic, and the base.Base classes

    *terminal:Here is the file where the Terminal class is stored. This class is in charge of getting the input and
    initializing everything in the application. This class has a similar functionality to the console.Console class.

********************
source/modules/terminal/argument:

    *argument: Argument_Handler: This class is supposed to replace the qt class in the console package. Its responsability
    is to parse the arguments sent by the terminal class, process the requests, and do the commands.

    *sockethandler: SocketThread:Socket Handler. It will call the callback everytime there's something to be read from the port specified.
    *timer: child of threading.Timer.

-----------------------

Changed Files:
-----------------------
*source/blendervr: Added the new commands to the argument parser.
*source/utils/console.py: Added the new commands, and the initialization of the new modes.

*source/modules/blendervr/console:
    -console.py : Added a is_terminal_mode property and made it false. So I can handle some calls from the logic package to
    the qt package.
    -logic/console.py: Handled some calls to the qt package. The qt calls will only run when the app is in GUI mode
    -logic/screen.py: Handled some calls to the qt package. The qt calls will only run when the app is in GUI mode
    -logic/screens.py: Handled some calls to the qt package. The qt calls will only run when the app is in GUI mode