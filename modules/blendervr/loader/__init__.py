# -*- coding: utf-8 -*-
# file: blendervr/loader/__init__.py

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
from ..tools import logger

ELEMENTS_MAIN_PREFIX = 'blenderVR:'


def main():
    if not is_creating_loader() and not is_console():
        sys.exit()


class Creator:
    def __init__(self, logger):

        self._logger = logger
        self._logger.setLevel('debug')

        self._input_blender_file = sys.argv[(sys.argv.index('--') + 1)]
        self._processed_files = []

    def process(self):
        if is_creating_loader():
            self._process(self._input_blender_file)

        elif is_console():
            print(get_output_blender_file(self._input_blender_file))

    def _process(self, filepath):
            import bpy

            # avoid infinite recursion
            if filepath in self._processed_files:
                return
            else:
                self._processed_files.append(filepath)

            bpy.ops.wm.open_mainfile(filepath=filepath)
            for scene in bpy.data.scenes:

                # Update frame_type of the scene, otherwise, there will be black borders ...
                scene.game_settings.frame_type = 'SCALE'

                # if the file has multiple cameras take only the active one
                camera = scene.camera

                if camera:
                    # init
                    SENSOR = ELEMENTS_MAIN_PREFIX + 'SensorInit'
                    bpy.ops.logic.sensor_add(type='ALWAYS', name=SENSOR,
                                                            object=camera.name)
                    sensor = camera.game.sensors.get(SENSOR)
                    sensor.use_pulse_true_level = False

                    CONTROLLER = ELEMENTS_MAIN_PREFIX + 'ControllerInit'
                    bpy.ops.logic.controller_add(type='PYTHON', name=CONTROLLER,
                                                            object=camera.name)
                    controller = camera.game.controllers.get(CONTROLLER)
                    controller.use_priority = True
                    controller.mode = 'MODULE'
                    controller.module = 'blendervr.init'

                    controller.link(sensor=sensor)

                    # loop
                    SENSOR = ELEMENTS_MAIN_PREFIX + 'SensorLoop'
                    bpy.ops.logic.sensor_add(type='ALWAYS', name=SENSOR,
                                                            object=camera.name)
                    sensor = camera.game.sensors.get(SENSOR)
                    sensor.use_pulse_true_level = True

                    CONTROLLER = ELEMENTS_MAIN_PREFIX + 'ControllerLoop'
                    bpy.ops.logic.controller_add(type='PYTHON', name=CONTROLLER,
                                                            object=camera.name)
                    controller = camera.game.controllers.get(CONTROLLER)
                    controller.mode = 'MODULE'
                    controller.module = 'blendervr.loop'

                    ACTUATOR = ELEMENTS_MAIN_PREFIX + 'Occulus:Filter'
                    bpy.ops.logic.actuator_add(type='FILTER_2D', name=ACTUATOR,
                                                            object=camera.name)
                    actuator = camera.game.actuators.get(ACTUATOR)
                    actuator.mode = 'CUSTOMFILTER'

                    TEXT = ELEMENTS_MAIN_PREFIX + 'Occulus:GLSL'
                    shader = bpy.data.texts.new(TEXT)
                    actuator.glsl_shader = shader
                    shader.from_string(SHADER_PROGRAM)

                    controller.link(sensor=sensor)
                    controller.link(actuator=actuator)

                    # we call the same processor file for all the files
                    # and all the scenes, it is up to the processor file
                    # to internally handle them differently

                    processor_files = sys.argv[(sys.argv.index('--') + 2):]

                    from blendervr.processor import _getProcessor
                    processor_class = _getProcessor(processor_files,
                                                    self._logger, True)
                    processor = processor_class(self)

                    processor.process(controller)

                    bpy.ops.wm.save_as_mainfile(copy=True,
                                        filepath=get_output_blender_file(filepath),
                                        relative_remap=True)


def get_output_blender_file(filepath):
    """Get the filepath of the processed .blend file"""
    output_blender_file = filepath.split('.')
    output_blender_file.insert(-1, 'vr')
    output_blender_file = '.'.join(output_blender_file)

    if not sys.platform.startswith('win'):
        output_blender_file = os.path.join(
              os.path.dirname(output_blender_file),
              '.' + os.path.basename(output_blender_file))

    return output_blender_file


SHADER_PROGRAM = """uniform sampler2D bgl_RenderedTexture;

const vec4 kappa = vec4(1.0,1.7,0.7,15.0);

uniform float screen_width;
uniform float screen_height;

const float scaleFactor = 0.9;

const vec2 leftCenter = vec2(0.25, 0.5);
const vec2 rightCenter = vec2(0.75, 0.5);

// Scales input texture coordinates for distortion.
vec2 hmdWarp(vec2 LensCenter, vec2 texCoord, vec2 Scale, vec2 ScaleIn) {
vec2 theta = (texCoord - LensCenter) * ScaleIn;
float rSq = theta.x * theta.x + theta.y * theta.y;
vec2 rvector = theta * (kappa.x +
                        kappa.y * rSq +
                        kappa.z * rSq * rSq +
                        kappa.w * rSq * rSq * rSq);
vec2 tc = LensCenter + Scale * rvector;
return tc;
}

bool validate(vec2 tc, int left_eye) {
//keep within bounds of texture
if ((left_eye == 1 && (tc.x < 0.0 || tc.x > 0.5)) ||
(left_eye == 0 && (tc.x < 0.5 || tc.x > 1.0)) ||
tc.y < 0.0 || tc.y > 1.0) {
return false;
}
return true;
}

void main() {
vec2 screen = vec2(screen_width, screen_height);

float as = float(screen.x / 2.0) / float(screen.y);
vec2 Scale = vec2(0.5, as);
vec2 ScaleIn = vec2(2.0 * scaleFactor, 1.0 / as * scaleFactor);

vec2 texCoord = gl_TexCoord[0].st;

vec2 tc = vec2(0);
vec4 color = vec4(0);

if (texCoord.x < 0.5) {
tc = hmdWarp(leftCenter, texCoord, Scale, ScaleIn );
color = texture2D(bgl_RenderedTexture, tc);
if (!validate(tc, 1))
color = vec4(0);
} else {
tc = hmdWarp(rightCenter, texCoord, Scale, ScaleIn);
color = texture2D(bgl_RenderedTexture, tc);
if (!validate(tc, 0))
color = vec4(0);
}
gl_FragColor = color;
}
"""

import os
if os.environ.get('READTHEDOCS', False) != 'True':
    main()
