import builtins
import imp
import os
import sys

def load_module(name, module):
    sys.modules[name] = module

def load_global(name, value):
    builtins.__dict__[name] = value

from . import (
        bge,
        bgl,
        blf,
        mathutils,
        OpenGL,
        PyQt4,
        PySide,
        )

# blender/bge modules
load_module('bge', bge)
load_module('bgl', bgl)
load_module('blf', blf)
load_module('mathutils', mathutils)

# other modules
load_module('OpenGL', OpenGL)
load_module('PyQt4', PyQt4)
load_module('PySide', PySide)

# globals
load_global('blenderVR_QT', 'PyQt4')
