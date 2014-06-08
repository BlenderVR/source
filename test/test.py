import time
from oculusvr import Rift

Rift.initialize()

rift = Rift()
time.sleep(0.1)
rift.start_sensor()
hmdDesc = rift.get_desc()
print hmdDesc.ProductName
print hmdDesc.MaxEyeFov[0].UpTan


while True:
    ss = rift.get_sensor_state()
    pose = ss.Predicted.Pose
    print "%10f   %10f   %10f   %10f" % ( \
        pose.Orientation.w, 
        pose.Orientation.x, 
        pose.Orientation.y, 
        pose.Orientation.z
    )
    time.sleep(0.5)

rift.destroy()
rift = None
Rift.shutdown()
