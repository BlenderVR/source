from OpenGL.GL import *
from OpenGL.GLUT import *
from math import sqrt
import time

from oculusvr import *


def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = sqrt(mag2)
        v = tuple(n / mag for n in v)
    return v

def dot(v1, v2):
    if (len(v1) != len(v2)):
        raise Exception("Can't dot two different sized vectors") 
    result = 0
    for i in range(0, len(v1)):
        result += v1[i] * v2[i]
    return result

def q_norm(q):
    return dot(q, q)

def q_inverse(q):
    norm = q_norm(q);
    if (norm <= 0.0):
        raise Exception("Invalid quaternion")
    invNorm = 1.0 / norm
    x, y, z, w = q
    return (-x * invNorm, -y * invNorm, -z * invNorm, w * invNorm)

def q_to_rotation_matrix(q):
    norm = q_norm(q)
    if norm == 1:
        s = 2 
    elif norm > 0:
        s = 2  / norm
    else:
        s = 0;
    x, y, z, w = q

    xs = x * s;
    ys = y * s;
    zs = z * s;
    xx = x * xs;
    xy = x * ys;
    xz = x * zs;
    xw = w * xs;
    yy = y * ys;
    yz = y * zs;
    yw = w * ys;
    zz = z * zs;
    zw = w * zs;

    return (1 - (yy + zz), (xy - zw), (xz + yw), 0,  
            (xy + zw), 1 - (xx + zz), (yz - xw), 0,  
            (xz - yw), (yz + xw), 1 - (xx + yy), 0, 
            0, 0, 0, 1)

class RiftApp():
    def __init__(self):
        Rift.initialize()
        self.rift = Rift()
        self.hmdDesc = self.rift.get_desc()
        # Workaround for a race condition bug in the SDK
        time.sleep(0.1)
        self.rift.start_sensor()

        self.fovPorts = (
            self.hmdDesc.DefaultEyeFov[0], 
            self.hmdDesc.DefaultEyeFov[1] 
        )
        self.projections = (
            ovrMat4ToTuple(Rift.get_perspective(self.fovPorts[0], 0.01, 1000, True)),
            ovrMat4ToTuple(Rift.get_perspective(self.fovPorts[1], 0.01, 1000, True))
        )
        self.eyeTextures = [ texture(), texture() ]
        for eye in range(0, 2):
            self.eyeTextures[eye].API = ovrRenderAPI_OpenGL
            size = self.eyeTextures[eye].TextureSize = self.rift.get_fov_texture_size(eye, self.fovPorts[eye])
            self.eyeTextures[eye].RenderViewport.Size = size 
            self.eyeTextures[eye].RenderViewport.Pos.x = 0
            self.eyeTextures[eye].RenderViewport.Pos.y = 0

    def create_window(self):
        # TODO figure out how to drop the window borders
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(self.hmdDesc.Resolution.w, self.hmdDesc.Resolution.h)
        glutInitWindowPosition(self.hmdDesc.WindowsPos.x, self.hmdDesc.WindowsPos.y)
        glutCreateWindow('Rift')


    @staticmethod
    def build_framebuffer(size):
        fbo =  glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        color = glGenTextures( 1 )
        glBindTexture( GL_TEXTURE_2D, color )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, size.w, size.h, 0, GL_RGB, GL_UNSIGNED_BYTE, None);
        glBindTexture( GL_TEXTURE_2D, 0 )
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color, 0);

        depth = glGenRenderbuffers(1)
        glBindRenderbuffer( GL_RENDERBUFFER, depth )
        glRenderbufferStorage(GL_RENDERBUFFER,
                              GL_DEPTH_COMPONENT,
                              size.w, size.h)
        glBindRenderbuffer( GL_RENDERBUFFER, 0 )
        glFramebufferRenderbuffer( GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth )

        if (GL_FRAMEBUFFER_COMPLETE != glCheckFramebufferStatus(GL_FRAMEBUFFER)):
            raise Exception("Bad framebuffer setup")
        glBindFramebuffer(GL_FRAMEBUFFER, 0 )
        return (fbo, color, depth)

    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.fbo = [ 0, 0 ]
        for eye in range(0, 2):
            self.fbo[eye], self.eyeTextures[eye].TexId, color = RiftApp.build_framebuffer(self.eyeTextures[eye].TextureSize)

        rc = ovrRenderAPIConfig()
        rc.API = ovrRenderAPI_OpenGL
        rc.RTSize = self.hmdDesc.Resolution
        rc.Multisample = 1
        self.eyeRenderDescs = self.rift.configure_rendering(rc, self.fovPorts)
        # Bug in the SDK leaves a program bound, so clear it
        glUseProgram(0)

    def render_frame(self):
        self.rift.begin_frame()
        for i in range(0, 2):
            eye = self.hmdDesc.EyeRenderOrder[i];
            pose = self.rift.begin_eye_render(eye)
    
            glMatrixMode(GL_PROJECTION)
            glLoadMatrixf(self.projections[eye])
    
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
    
            eyeOffset = ovrVec3ToTuple(self.eyeRenderDescs[eye].ViewAdjust)
            position = ovrVec3ToTuple(pose.Position)
            orientation = ovrQuatToTuple(pose.Orientation)
            orientation = q_to_rotation_matrix(orientation) 
    
            # Apply the per-eye offset
            glTranslate(eyeOffset[0], eyeOffset[1], eyeOffset[2])
            # Apply the head orientation
            glMultMatrixf(orientation)
            # Apply the head position
            glTranslate(-position[0], -position[1], -position[2])
            # apply the camera position
            glMultMatrixf(self.modelview)

            # Active the offscreen framebuffer and render the scene
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbo[eye])
            size = self.eyeTextures[eye].RenderViewport.Size
            glViewport(0, 0, size.w, size.h)
            self.render_scene()
            glBindFramebuffer(GL_FRAMEBUFFER, 0)

            self.rift.end_eye_render(eye, self.eyeTextures[eye], pose)
        self.rift.end_frame()

    def render_scene(self):
        return

    def finalize(self):
        self.rift.stop_sensor()
        self.rift.destroy()
        self.rift = None
        Rift.shutdown()




