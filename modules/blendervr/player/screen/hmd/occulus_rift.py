# -*- coding: utf-8 -*-
# file: blendervr/player/screen/hmd/occulus_rift.py

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

import mathutils
import bge
from . import base
from ... import exceptions

""" @package hmd
Manager of Occulus Rift screens with blenderVR
"""

warning_for_unsure_projection_displayed = False

class Device(base.Device):

    def __init__(self, parent, configuration):
        super(Device, self).__init__(parent, configuration)
        self._plugin = None

    def start(self):
        import sys

        self._plugin = self.blenderVR.getPlugin('occulus_rift')
        if self._plugin is None:
            self.logger.error("Occulus Rift plugin (occulus_rift) not setup in the configuration file, HMD device won't work")
            self.blenderVR.quit("Occulus Rift plugin (occulus_rift) not setup in the configuration file, HMD device won't work")
            return

        try:
            import bge

            width = bge.render.getWindowWidth()
            height = bge.render.getWindowHeight()

            cont = bge.logic.getCurrentController()

            cont.owner["screen_width"] = width
            cont.owner["screen_height"] = height

            ELEMENTS_MAIN_PREFIX = 'blenderVR:'
            ACTUATOR = ELEMENTS_MAIN_PREFIX + 'Occulus:Filter'

            actuator = cont.actuators.get(ACTUATOR)
            if not actuator:
                self.logger.error('Error: Occulus Rift 2D Filter Actuator not found ({0})'.format(ACTUATOR))
            else:
                cont.activate(actuator)

        except Exception as err:
            self.logger.error(err)


    def run(self):
        if self._plugin == None:
            return

        try:
            import bge
            from mathutils import Euler
            from math import pi

            from game_engine_rift.rift import PyRift

            if not hasattr(bge.logic, 'rift'):
                bge.logic.rift = PyRift()
                euler = Euler((0, 0, 0), 'XYZ')
            else:
                self._poll(bge.logic.rift)
                euler = bge.logic.rotation.to_euler()

            """
            TODO: the following is the part we need to change later
            so it uses our internal classes to access the navigation
            (instead of by passing it entirely)
            """
            scene = bge.logic.getCurrentScene()
            camera = scene.active_camera
            fix = Euler((-pi/2, 0, 0), 'XYZ')

            rot = Euler((-euler.z, euler.y, -euler.x), 'XYZ')
            rot.rotate(fix)
            camera.worldOrientation = rot

        except Exception as err:
            self.logger.error(err)

    def _poll(self, rift):
        import bge
        from mathutils import Quaternion

        rift.poll()
        bge.logic.rotation = Quaternion((rift.rotation[0],
                rift.rotation[1],
                rift.rotation[2],
                rift.rotation[3]))
