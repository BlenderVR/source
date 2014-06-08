#! /usr/bin/env python
import sys, time
from math import sqrt, sin, cos, acos
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from oculusvr import *

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

def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z

def q_conjugate(q):
    q = normalize(q)
    w, x, y, z = q
    return (w, -x, -y, -z)

def qv_mult(q1, v1):
    v1 = normalize(v1)
    q2 = (0.0,) + v1
    return q_mult(q_mult(q1, q2), q_conjugate(q1))[1:]

def axisangle_to_q(v, theta):
    v = normalize(v)
    x, y, z = v
    theta /= 2
    w = cos(theta)
    x = x * sin(theta)
    y = y * sin(theta)
    z = z * sin(theta)
    return w, x, y, z

def q_to_axisangle(q):
    w, v = q[0], q[1:]
    theta = acos(w) * 2.0
    return normalize(v), theta

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
    w, x, y, z = q
    return (w * invNorm, -x * invNorm, -y * invNorm, -z * invNorm)

def q_to_rotation_matrix(q):
    norm = q_norm(q)
    if norm == 1:
        s = 2 
    elif norm > 0:
        s = 2  / norm
    else:
        s = 0;
    w, x, y, z = q

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

def translate(v):
    glTranslate(v.x, v.y, v.z)

def rotate(q):
    q = (q.w, q.x, q.y, q.z)
    m = q_to_rotation_matrix(q)
    glMultMatrixf(m)

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
    light_ambient = [0.0, 0.0, 0.0, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [1.0, 1.0, 1.0, 0.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 5,
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


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity()
    if w <= h:
        gluPerspective(80, 1, 0.01, 100)
        #glOrtho(-2.5, 2.5, -2.5 * h / w, 2.5 * h / w, -10.0, 10.0)
    else:
        gluPerspective(80, 1, 0.01, 100)
        #glOrtho(-2.5 * w / h, 2.5 * w / h, -2.5, 2.5, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)

def renderScene():
    glClearColor(0.2, 0.2, 0.2, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotatef(20.0, 1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(-0.75, 0.5, 0.0);
    glRotatef(90.0, 1.0, 0.0, 0.0)
    glutSolidTorus(0.275, 0.85, 15, 15)
    glPopMatrix()
 
    glPushMatrix()
    glTranslatef(-0.75, -0.5, 0.0);
    glRotatef (270.0, 1.0, 0.0, 0.0)
    glutSolidCone(1.0, 2.0, 15, 15)
    glPopMatrix()
 
    glPushMatrix()
    glTranslatef(0.75, 0.0, -1.0)
    glutSolidSphere(1.0, 15, 15)
    glPopMatrix()
    glPopMatrix()


def display():
    rift.begin_frame()
    for i in range(0, 2):
        eye = hmdDesc.EyeRenderOrder[i];
        pose = rift.begin_eye_render(eye)

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(projections[eye])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #
        # TODO make a better scene content with a color cube to validate 
        # this order of operations
        #
        # Apply the per-eye offset
        translate(eyeRenderDescs[eye].ViewAdjust)
        # Apply the head orientation
        rotate(pose.Orientation)
        # Apply the head position
        translate(pose.Position)
        glMultMatrixf(modelview)

        glBindFramebuffer(GL_FRAMEBUFFER, fbo[eye])
        size = eyeTextures[eye].RenderViewport.Size
        glViewport(0, 0, size.w, size.h)
        renderScene()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        rift.end_eye_render(eye, eyeTextures[eye], pose)
    rift.end_frame()
    glutSwapBuffers()
    glutPostRedisplay()


def ovrMat4ToTuple(m):
    mm = []
    for i in range(0, 4):
        for j in range(0, 4):
            mm.append(m.M[j][i])
    return tuple(mm)

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

glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutDisplayFunc(display)
glutMainLoop()

