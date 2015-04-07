.. _processor-files-osc-api:

#######
OSC API
#######

How to use the OSC API integrated in blenderVR.

Introduction
************

OSC is integrated as a blenderVR plugin, to be defined in the .xml configuration
file.
The OSC API is e.g. used for blenderVR synchornization with the
Max/MSP based `blenderVR Sound Engine <https://blendervr.limsi.fr/doku.php?id=addons>`_.
For example, in the default main.xml configuration file, you'll see:

.. code-block:: xml

  <plugins>

    <osc host='localhost' port='3819' configuration='Laptop SPAT'>

      <user listener='Binaural 1' viewer='user A' />
      <!-- <user listener='Binaural 2' viewer='user B' /> -->
      <user listener='Ambisonic' />
      <user listener='Stereo' />
      <!-- <room warmth='32' /> -->

    </osc>

  </plugins>

Every parameter defined in these lines will be sent to the OSC client
at blenderVR startup (but for osc host and port).

Received by the OSC client at blenderVR start:

.. code-block::
    /global configuration Laptop SPAT
    /user 0 name Binaural 1
    /user 1 name Ambisonic
    /user 2 name Stereo

The configuration flag allows to dynamically parametrize the OSC client
to fit the requirements of the current architecture.

user flags allow to dynamically define a routing table between blenderVR users
and OSC users (here user 0 in OSC client will be attached to Binaural 1 i.e. user A
in blenderVR, e.g. for position update).

.. code-block:: python

    OSC = self.blenderVR.getPlugin('osc')


with self being the blenderVR `processor <../../processor-file/examples.html>`_ object grants access to blenderVR OSC module and its API (OSC in python code bellow refers to this module).

From there, blenderVR OSC API proposes 4 different class of messages: global, user, object and objectUser.

Global Messages
***************

Global messages can be used for global configuration of the Sound Engine (e.g. global volume, start, etc.).

.. code-block:: python

    osc_global = OSC.getGlobal()
    osc_global.start(True)
    osc_global.mute(True)
    osc_global.volume('%45')

will send the following messages to the Sound Engine:

.. code-block:: bash

    /global start 1
    /global mute 1
    /global volume %45

with volume being either absolute balue ('%45') or +/- relative add ('+3', '-3').


User Messages
*************

User messages can be used for user specific configuration of the Sound Engine (e.g. user volume, user start, etc.).
See OSC users as listeners, or rather as the media + rendering technique that produce a sound (an ambisonic system, a binaural headset, etc.).

.. code-block:: python

    osc_user = OSC.getUser('Binaural 1')
    # or equivalently
    bvr_user = self.blenderVR.getUserByName('user A')
    osc_user = OSC.getUser(bvr_user)
    # --
    osc_user.start(True)
    osc_user.mute(True)
    osc_user.volume('%45')

The first line grants access to the OSC user named "Binaural 1" in the configuration file (attached to blenderVR user A, see above). Thanks to the definition of user / listener in the configuration file, each blenderVR user position/orientation ('user A' here) will be synchronized form blenderVR to the sound rendering engine.

The next lines will send the following messages to the Sound Engine:

.. code-block:: bash

    /user 1 start 1
    /user 1 mute 1
    /user 1 volume %45

and blenderVR will constantly update osc user position with messages like:

.. code-block:: bash

    /user 1 position 1. 0. 0. 0. 0. -1. -0. 0. 0. 0. -1. 0. 0. 0. 0. 1.

where the 16 floats represent the 4x4 homogeneous Matrix of user position/orientation in the virtual world.

Object Messages
***************

Object messages can be used for object specific configuration of the Sound Engine (e.g. object volume, object start, etc.).
See OSC objects as a virtual sound source instantiated in the Sound Engine, that will be attached to a blenderVR object (e.g. a blender KX_Game_Object) in the scene and eventually heard by one/many OSC user/listener (see objectUser messages bellow).

.. code-block:: python

    scene = bge.logic.getCurrentScene()
    kx_object = scene.objects['Cube']
    osc_object = OSC.getObject(kx_object)
    osc_object.sound('HeyPachuco.wav')
    osc_object.start(True)
    osc_object.mute(False)
    osc_object.volume('%45')

The first line grants access to the OSC object that will be attached to the KX_GameObject 'Cube' in the blender scene. This first line triggers a callback that
will synchronize the object position in the
The next lines will send the following messages to the Sound Engine:

.. code-block:: bash

    /object 1 sound HeyPachuco.wav
    /object 1 start 1
    /object 1 mute 0
    /object 1 volume %45

and blenderVR will constantly update osc object position with messages like:

.. code-block:: bash

    /object 1 position 0.54156 0.132934 -0.830085 0. -0.840592 0.07291 -0.536739 0. -0.01083 0.98844 0.151228 0. -11.07954 0.250764 -14.501128 1.

ObjectUser Messages
*******************

This class of messages allow to dynamically route object sounds to osc users (listeners) audio input. basically, sending:

.. code-block:: bash

    /objectUser 1 0 mute 0

will tell the sound engine to route osc object 1 to osc user 0 (Binaural 1 here, see above), hence the listener Binaural 1 will hear the sound of object 1.

.. code-block:: python
    scene = bge.logic.getCurrentScene()
    kx_object = scene.objects['Cube']
    osc_object = OSC.getObject(kx_object)

    osc_user = OSC.getUser('Binaural 1')

    OSC.getObjectUser(osc_object, osc_user)
    # OSC.getObjectUser will automatically send a mute(False),
    # the line bellow is not really required
    osc_objectUser.mute(False)
    osc_objectUser.volume('%50')

The line 'OSC.getObjectUser(osc_object, osc_user)' grants access to the OSC objectUser that will control the link between the sound from the osc object
(attached to the blender object 'Cube') to the osc user 'Binaural 1'.
The next two lines will send the following messages to the Sound Engine:

.. code-block:: bash

    /objectUser 1 0 mute 0
    /objectUser 1 0 volume %50


Example
*******

The basic-osc.blend in the blenderVR `samples <http://blender-vr-manual.readthedocs.org/installation/installation.html#download-samples-scenes>`_ will send the following OSC messages to the Sound Engine (it's actually the code in the basic-osc.processor.py along with the osc plugin definition in the //blender-vr/configuration/main.xml configuration file that will provoke their envoy):

.. code-block:: bash

    /global configuration Laptop SPAT
    /global volume %40
    /global start 1
    /global mute 0
    /object 1 sound HeyPachuco.wav
    /object 1 loop 1
    /object 1 volume %45
    /object 1 start 1
    /object 1 position 0.54156 0.132934 -0.830085 0. -0.840592 0.07291 -0.536739 0. -0.01083 0.98844 0.151228 0. -11.07954 0.250764 -14.501128 1.
    /object 1 mute 0
    /user 2 name Ambisonic
    /user 2 hrtf 0
    /user 2 volume %50
    /user 2 position
    /user 2 start 0
    /user 2 mute 0
    /user 2 warmth 0
    /user 2 brightness 0
    /user 2 presence 0
    /user 2 reverb_volume 0
    /user 2 running_reverb 0
    /user 2 late_reverb 0
    /user 2 envelop 0
    /user 2 heavyness 0
    /user 2 livelyness 0
    /user 0 name Binaural 1
    /user 0 hrtf 0
    /user 0 volume %80
    /user 0 position 1. 0. 0. 0. 0. -1. -0. 0. 0. 0. -1. 0. 0. 0. 0. 1.
    /user 0 start 1
    /user 0 mute 0
    /user 0 warmth 0
    /user 0 brightness 0
    /user 0 presence 0
    /user 0 reverb_volume 0
    /user 0 running_reverb 0
    /user 0 late_reverb 0
    /user 0 envelop 0
    /user 0 heavyness 0
    /user 0 livelyness 0
    /user 1 name Binaural 2
    /user 1 hrtf 0
    /user 1 volume %50
    /user 1 position 1. 0. 0. 0. 0. -1. -0. 0. 0. 0. -1. 0. 0. 0. 0. 1.
    /user 1 start 0
    /user 1 mute 0
    /user 1 warmth 0
    /user 1 brightness 0
    /user 1 presence 0
    /user 1 reverb_volume 0
    /user 1 running_reverb 0
    /user 1 late_reverb 0
    /user 1 envelop 0
    /user 1 heavyness 0
    /user 1 livelyness 0
    /user 3 name Stereo
    /user 3 hrtf 0
    /user 3 volume %50
    /user 3 position
    /user 3 start 0
    /user 3 mute 0
    /user 3 warmth 0
    /user 3 brightness 0
    /user 3 presence 0
    /user 3 reverb_volume 0
    /user 3 running_reverb 0
    /user 3 late_reverb 0
    /user 3 envelop 0
    /user 3 heavyness 0
    /user 3 livelyness 0
    /objectUser 1 0 volume %50
    /objectUser 1 0 mute 0
    /object 1 position 0.529771 0.133939 -0.837498 0. -0.848072 0.071046 -0.525097 0. -0.01083 0.98844 0.151228 0. -11.182952 0.225004 -14.340163 1.
    /object 1 position 0.517878 0.134918 -0.844748 0. -0.855386 0.069169 -0.513353 0. -0.01083 0.98844 0.151228 0. -11.284078 0.199052 -14.177782 1.

