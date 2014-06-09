#! /usr/bin/env python
import time
from math import sqrt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from oculusvr import *
#from RiftApp import *

fovPorts = [ fov_port(), fov_port() ]
projections = [ mat4(), mat4() ]
eyeTextures = [texture(), texture() ]
fbo = [ 0, 0 ]
eyeRenderDescs = [ eye_render_desc(), eye_render_desc() ]
modelview = ()

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

def keyboard(key, x, y):
    if key == chr(27):
        global rift
        rift.stop_sensor()
        rift.destroy()
        rift = None
        Rift.shutdown()
        sys.exit(0)

#  Initialize material property and light source.
def init():
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 0.5,
              0, 0, 0,
              0, 1, 0)
    global modelview
    modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()

    for eye in range(0, 2):
        fbo[eye] =  glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo[eye])
        color = eyeTextures[eye].TexId = glGenTextures( 1 )
        glBindTexture( GL_TEXTURE_2D, color )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 
                       size.w, size.h,
                       0, GL_RGB, GL_UNSIGNED_BYTE, None);
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

    rc = ovrRenderAPIConfig()
    rc.API = ovrRenderAPI_OpenGL
    rc.RTSize = hmdDesc.Resolution
    rc.Multisample = 1
    global eyeRenderDescs
    eyeRenderDescs = rift.configure_rendering(rc, fovPorts)
    glUseProgram(0)

def drawColorCube(size = 1.0):
    p = size / 2.0
    n = -p
    glBegin(GL_QUADS)

    # front
    glColor3f(1, 1, 0, 1)
    glVertex3f(n, n, n)
    glVertex3f(p, n, n)
    glVertex3f(p, p, n)
    glVertex3f(n, p, n)
    # back
    glColor3f(0, 0.2, 1, 1)
    glVertex3f(n, n, p)
    glVertex3f(p, n, p)
    glVertex3f(p, p, p)
    glVertex3f(n, p, p)
    # right
    glColor3f(1, 0, 0, 1)
    glVertex3f(p, n, n)
    glVertex3f(p, n, p)
    glVertex3f(p, p, p)
    glVertex3f(p, p, n)
    # left
    glColor3f(0, 1, 1, 1)
    glVertex3f(n, n, n)
    glVertex3f(n, n, p)
    glVertex3f(n, p, p)
    glVertex3f(n, p, n)
    # top
    glColor3f(0, 1, 0, 1)
    glVertex3f(n, p, n)
    glVertex3f(p, p, n)
    glVertex3f(p, p, p)
    glVertex3f(n, p, p)
    # bottom
    glColor3f(1, 0, 1, 1)
    glVertex3f(n, n, n)
    glVertex3f(p, n, n)
    glVertex3f(p, n, p)
    glVertex3f(n, n, p)
    glEnd()

def renderScene():
    glClearColor(0.2, 0.2, 0.2, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawColorCube(0.06)
#     glPushMatrix()
#     glRotatef(20.0, 1.0, 0.0, 0.0)
#     glPushMatrix()
#     glTranslatef(-0.75, 0.5, 0.0);
#     glRotatef(90.0, 1.0, 0.0, 0.0)
#     glutSolidTorus(0.275, 0.85, 15, 15)
#     glPopMatrix()
#  
#     glPushMatrix()
#     glTranslatef(-0.75, -0.5, 0.0);
#     glRotatef (270.0, 1.0, 0.0, 0.0)
#     glutSolidCone(1.0, 2.0, 15, 15)
#     glPopMatrix()
#  
#     glPushMatrix()
#     glTranslatef(0.75, 0.0, -1.0)
#     glutSolidSphere(1.0, 15, 15)
#     glPopMatrix()
#     glPopMatrix()


def display():
    rift.begin_frame()
    for i in range(0, 2):
        eye = hmdDesc.EyeRenderOrder[i];
        pose = rift.begin_eye_render(eye)

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(projections[eye])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        eyeOffset = ovrVec3ToTuple(eyeRenderDescs[eye].ViewAdjust)
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
        glMultMatrixf(modelview)

        # Active the offscreen framebuffer and render the scene
        glBindFramebuffer(GL_FRAMEBUFFER, fbo[eye])
        size = eyeTextures[eye].RenderViewport.Size
        glViewport(0, 0, size.w, size.h)
        renderScene()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        rift.end_eye_render(eye, eyeTextures[eye], pose)
    rift.end_frame()
    glutSwapBuffers()
    glutPostRedisplay()

Rift.initialize()
rift = Rift()
hmdDesc = rift.get_desc()
# Workaround for a race condition bug in the SDK
time.sleep(0.1)
rift.start_sensor()

for eye in range(0, 2):
    fovPorts[eye] = hmdDesc.DefaultEyeFov[eye]
    projections[eye] = ovrMat4ToTuple(Rift.get_perspective(fovPorts[eye], 0.01, 1000, True))
    eyeTextures[eye].API = ovrRenderAPI_OpenGL
    size = eyeTextures[eye].TextureSize = rift.get_fov_texture_size(eye, fovPorts[eye])
    eyeTextures[eye].RenderViewport.Size = size 
    eyeTextures[eye].RenderViewport.Pos.x = 0
    eyeTextures[eye].RenderViewport.Pos.y = 0

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
glutInitWindowSize (hmdDesc.Resolution.w, hmdDesc.Resolution.h)
glutInitWindowPosition(hmdDesc.WindowsPos.x, hmdDesc.WindowsPos.y)
glutCreateWindow('scene')

init()

#glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutDisplayFunc(display)
glutMainLoop()

