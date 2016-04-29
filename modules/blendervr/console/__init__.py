# -*- coding: utf-8 -*-
# file: blendervr/console/__init__.py

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

import sys
import os

from .. import *
from . import logic


def main():
    if not is_console():
        import bge
        bge.logic.endGame()
        sys.exit()


def stripAnchor(anchor, path):
    """Compute file path to have a relative path to parent dir anchor.

    If path is not a subpath of anchor, it is returned unchanged
    with a bool False flag. 
    If path is a subpath of anchor, it is returned relative to anchor
    with a bool flag True.

    If path is None, simply return None.
    If anchor is None, return path and bool flag False indicating inchanged.

    :param anchor: root part of path to remove.
    :type anchor: string
    :param path: complete path to strip anchor root path.
    :type path: string
    :rtype: (string, bool)
    :return: relative path from anchor, indicator of modification
    """
    if path is None:
        return None
    if anchor is not None:
        relpath = os.path.relpath(path, anchor)
        if not relpath.startswith('..'):
            return (relpath, True)
    return (path, False)


def unstripAnchor(anchor, path):
    """Re-insert removed anchor root at begin of path.

    Warning: Here path is not a simple string as in stripAnchor() call,
    its the result of this call: (string, bool).

    If path is None, simply return None.
    If path has not been modified (path[1] is False), then simply
    return the path strting as is.
    Else prepend anchor to the path string.

    :param anchor: root part of path to re-insert.
    :type anchor: string
    :param path: alue returned from stripAnchor call()
    :type path: (string, bool)
    :rtype: string
    :return: absolute path including anchor
    """
    if path is None:
        return None
    if path[1] and anchor is not None:
        return "/".join((anchor, path[0]))
    return path[0]


# Environment variable set by documentation processing, used to avoid
# execution of blendervr when we are just importing for generating
# documentation.
# Package bvr is a Blender tool, its presence in modules indicate that
# we are not in the blenderplayer context but in an interactive Blender
# session using the BlenderVR bvr tool.
# In these two cases, we DONT start the BlenderVR machinery.
if os.environ.get('READTHEDOCS', False) != 'True' and (
        'bvr' not in sys.modules or 'BVR_LOADER_CREATION' in os.environ):
    main()
