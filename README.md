python-ovrsdk
=============

##### Cross-platform wrapper for the Oculus VR SDK C API

Actually, it's not terribly cross-platform, yet. It's only supported 
on windows because the current release of the SDK is only available
for Windows. As soon as Linux and OSX becomes available, I'll be updating
it to support them.

##### Installation
Keep it simple. Download the package and drop it in your project. Done.

##### Use

from ovrsdk import *

ovr_Initialize()
hmd = ovrHmd_Create(0)
hmdDesc = ovrHmdDesc()
ovrHmd_GetDesc(hmd, byref(hmdDesc))

ovrHmd_StartSensor(hmd, ovrHmdCap_Orientation | ovrHmdCap_YawCorrection |
	ovrHmdCap_Position | ovrHmdCap_LowPersistence,
	ovrHmdCap_Orientation);

ss = ovrHmd_GetSensorState(hmd, 0.0);
if (ss.StatusFlags & (ovrStatus_OrientationTracked | ovrStatus_PositionTracked)):
	pose = ss.Predicted.Pose;
	print "%10f   %10f   %10f   %10f" % ( \
		pose.Orientation.w, 
		pose.Orientation.x, 
		pose.Orientation.y, 
		pose.Orientation.z
	)

ovrHmd_Destroy(hmd)
ovr_Shutdown()

##### Credits

* Oculus VR, for being awesome and making a C API.
* ctypesgen (https://code.google.com/p/ctypesgen/)

