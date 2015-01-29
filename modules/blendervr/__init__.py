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
Main module of the Blender-VR application
"""


# Beware: you must alswo change blenderVR console executable to change the
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
    if is_virtual_environment():
        import bge
        bge.logic.blenderVR.run()
    else:
        pass


def main():
    if is_virtual_environment():
        try:
            import bge
            from .player import Main

            if not hasattr(bge.logic, "blenderVR"):
                bge.logic.blenderVR = Main()
        except:
            pass

import os
# Environment variable set by documentation processing, used to avoid
#
if os.environ.get('READTHEDOCS', False) != 'True':
    main()
