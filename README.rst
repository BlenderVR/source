python-ovrsdk
=============

Cross-platform wrapper for the Oculus VR SDK C API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Works on Linux and Windows. Precompiled Oculus VR SDK shared library included, so just install it and go.

Installation
~~~~~~~~~~~~

::

    pip install python-ovrsdk

Use
~~~

.. code:: python

    import time
    from ovrsdk import *

    ovr_Initialize()
    hmd = ovrHmd_Create(0)
    hmdDesc = ovrHmdDesc()
    ovrHmd_GetDesc(hmd, byref(hmdDesc))
    print hmdDesc.ProductName
    ovrHmd_StartSensor( \
      hmd, 
      ovrSensorCap_Orientation | 
      ovrSensorCap_YawCorrection, 
      0
    )

    while True:
      ss = ovrHmd_GetSensorState(hmd, ovr_GetTimeInSeconds())
      pose = ss.Predicted.Pose
      print "%10f   %10f   %10f   %10f" % ( \
        pose.Orientation.w, 
        pose.Orientation.x, 
        pose.Orientation.y, 
        pose.Orientation.z
      )
      time.sleep(0.016)

Output:
'''''''

::

    Oculus Rift DK1
      1.000000     0.000000     0.000000     0.000000
      0.992197     0.124599    -0.000122     0.004537
      0.992192     0.124621     0.000212     0.004909
      0.992168     0.124852     0.000430     0.003814
      0.992249     0.124183    -0.000085     0.004583
      0.992164     0.124768     0.000595     0.006597
      0.992263     0.124067    -0.000134     0.004630
      0.992276     0.123989     0.000412     0.003885
      0.992275     0.123943     0.000745     0.005242
      0.992168     0.124891     0.001882     0.001237
      0.992377     0.123240    -0.000291     0.000687
      0.992316     0.123698    -0.000632     0.002837
      0.991962     0.126352     0.000245     0.006768
    ...

Credits
~~~~~~~

-  Oculus VR, for being awesome and making a C API for their SDK.
-  The authors of ctypesgen (https://code.google.com/p/ctypesgen/) for
   their outstanding ctypes wrapper generator.