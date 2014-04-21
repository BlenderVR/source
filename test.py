import time
from ovrsdk import *

ovr_Initialize()
hmd = ovrHmd_Create(0)
hmdDesc = ovrHmdDesc()
ovrHmd_GetDesc(hmd, byref(hmdDesc))
print hmdDesc.ProductName
ovrHmd_StartSensor( \
	hmd, ovrHmdCap_Orientation | ovrHmdCap_YawCorrection |
	ovrHmdCap_Position | ovrHmdCap_LowPersistence,
	ovrHmdCap_Orientation
)

while True:
	ss = ovrHmd_GetSensorState(hmd, 0.0)
	pose = ss.Predicted.Pose
	print "%10f   %10f   %10f   %10f" % ( \
		pose.Orientation.w, 
		pose.Orientation.x, 
		pose.Orientation.y, 
		pose.Orientation.z
	)
	time.sleep(0.1)

ovrHmd_Destroy(hmd)
ovr_Shutdown()
