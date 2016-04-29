# -*- coding: utf-8 -*-
# file: blendervr/__init__.py

## Copyright (C) LIMSI-CNRS (2014)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer,
##
## This software is a computer program whose purpose is to distribute
## blender to render on Virtual Reality device systems.
##
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use,
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info".
##
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability.
##
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or
## data to be ensured and,  more generally, to use and operate it in the
## same conditions as regards security.
##
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
##

"""
Main module of the BlenderVR application
"""

import sys
import os

# Beware: you must alswo change BlenderVR console executable to change the
# profile pickle file to load
version = 1.0


def is_virtual_environment():
    """
    Check if the Blender Game Engine is available.

    :rtype: bool
    """
    try:
        import bge
        return True
    except:
        return False


def is_creating_loader():
    """
    Check if BPY is available.

    :rtype: bool
    """
    try:
        import bpy
        # With integration of BlenderVR as a Blender tool, we can have
        # bpy importable (ie. is_creating_loader() True) but being in the
        # console with the bvr package tool…
        # Use an environment variable given to Blender to detect that
        # we are using it to patch the scene xxx.blend and generate the
        # corresponding .xxx.blend file.
        if 'bvr' in os.modules and 'BVR_LOADER_CREATION' not in os.environ:
            return False
        return True
    except:
        return False


def is_console():
    """
    Check if it is in console mode.

    :rtype: bool
    """
    return not is_virtual_environment() and not is_creating_loader()


def run():
    """Run VR rendering environment from bound bge.logic.BlenderVR object.
    """
    if is_virtual_environment():
        import bge
        bge.logic.BlenderVR.run()
    else:
        pass


def main():
    """In case of virtual environment rendering, bind machinery inside bge.logic.BlenderVR.
    """
    if is_virtual_environment():
        try:
            import bge
            from .player import Main
            bge.logic.BlenderVR = Main()
        except:
            pass

# Environment variable set by documentation processing, used to avoid
# execution of blendervr when we are just importing for generating
# documentation.
# Package bvr is a Blender tool, its presence in modules indicate that
# we are not in the blenderplayer context but in an interactive Blender
# session using the BlenderVR bvr tool.
# In these two cases, we DONT start the BlenderVR machinery.


if os.environ.get('READTHEDOCS', 'False') != 'True' and (
        'bvr' not in sys.modules or 'BVR_LOADER_CREATION' in os.environ):
    main()

