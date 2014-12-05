.. _processor-files-examples:

############
 Examples
############

For more examples, check the ``processor`` files in the `Samples Repository <https://github.com/BlenderVR/samples>`_ of the Blender-VR project.

Basic Example
*************

This is a basic ``processor`` file which can be considered a barebone and a start point for your own. All it does is to syncronize all the objects between the master and the slaves machines. 

.. code-block:: python
   :linenos:

    import blendervr

    if blendervr.is_console():
        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, console):
                global try_wait_user_name, try_chooser, try_console_arc_balls
                super(Processor, self).__init__(console)

            def useLoader(self):
                return True

    elif blendervr.is_creating_loader():
        import bpy

        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, creator):
                super(Processor, self).__init__(creator)

    elif blendervr.is_virtual_environment():
        import bge

        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, parent):
                super(Processor, self).__init__(parent)

                if self.blenderVR.isMaster():
                    self.blenderVR.getSceneSynchronizer().\
                            getItem(bge.logic).activate(True, True)


The file is split in three parts:

 1. `Console`_
 2. `Update Loader`_
 3. `Virtual Environment`_

The ``processor`` file is called three times, and each time a section of it is called.

Console
=======
The console part of the code is called first by the ``console``.
This runs before your ``.blend`` file is even loaded.
The ``useLoader()`` determines if you need Blender-VR to modify your ``.blend`` on-the-fly.

Most of the time this won't need to change. The exception is when the file being loaded was
already modified to work with Blender-VR (e.g., the file generated on-the-fly after running it once).

.. code-block:: python
   :lineno-start: 3

    if blendervr.is_console():
        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, console):
                global try_wait_user_name, try_chooser, try_console_arc_balls
                super(Processor, self).__init__(console)

            def useLoader(self):
                return True

Update Loader
=============
If a project requires specific changes in the ``.blend`` file they are introduced here.
This is the place where a specific ``Actuator`` can be added for a Head-Mounted display for example.

.. code-block:: python
   :lineno-start: 12

    elif blendervr.is_creating_loader():
        import bpy

        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, creator):
                super(Processor, self).__init__(creator)

Virtual Environment
===================
This part of the code is called when the ``.blend`` file is loaded in the Blender Game Engine.
The most basic usage is to syncronize all the scene objects, as it's being done here.

.. code-block:: python
   :lineno-start: 19

    elif blendervr.is_virtual_environment():
        import bge

        class Processor(blendervr.processor.getProcessor()):
            def __init__(self, parent):
                super(Processor, self).__init__(parent)

                if self.blenderVR.isMaster():
                    self.blenderVR.getSceneSynchronizer().\
                            getItem(bge.logic).activate(True, True)

