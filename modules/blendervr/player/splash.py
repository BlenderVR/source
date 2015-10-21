# -*- coding: utf-8 -*-
# file: blendervr/player/splash.py

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

import time
import bge
import blf
import os
import mathutils
from bgl import *
from . import base

ECG_VALUES = [2.2115759e+00, 1.9184524e+00, 1.6262298e+00, 1.3363817e+00,
              1.0457467e+00, 8.7953729e-01, 8.0215353e-01, 7.2426229e-01,
              6.5531316e-01, 7.2484014e-01, 8.0165860e-01, 8.7841227e-01,
              8.9891580e-01, 8.9938683e-01, 9.0013088e-01, 9.0042507e-01,
              8.9932180e-01, 9.4631408e-01, 1.0210519e+00, 1.0902796e+00,
              1.1501810e+00, 1.1975850e+00, 1.2304606e+00, 1.2475264e+00,
              1.2478137e+00, 1.2309090e+00, 1.1975449e+00, 1.1497013e+00,
              1.0900498e+00, 1.0214188e+00, 9.4676607e-01, 8.9919702e-01,
              8.9986325e-01, 8.9991225e-01, 8.9988388e-01, 8.9977460e-01,
              8.9966892e-01, 8.9969241e-01, 8.9980904e-01, 8.9988400e-01,
              9.0185543e-01, 9.2238531e-01, 9.3397361e-01, 9.3126973e-01,
              9.1529574e-01, 8.9942898e-01, 8.9962413e-01, 8.9978944e-01,
              8.9995322e-01, 8.9989238e-01, 8.9966710e-01, 8.9959321e-01,
              8.9979372e-01, 8.9998970e-01, 8.9988168e-01, 8.9960574e-01,
              8.9957540e-01, 8.9987410e-01, 9.0006866e-01, 8.9979595e-01,
              8.9937733e-01, 8.9969153e-01, 9.1359251e-01, 9.9441355e-01,
              1.0596300e+00, 1.1037278e+00, 1.1246771e+00, 1.1277361e+00,
              1.1011566e+00, 1.0485388e+00, 9.7126260e-01, 8.9859989e-01,
              8.9977939e-01, 9.0055926e-01, 8.9983003e-01, 8.9861560e-01,
              8.9962911e-01, 9.4572544e-01, 1.2391061e+00, 1.5307464e+00,
              1.8201066e+00, 2.1104914e+00, 2.4091746e+00, 2.3016856e+00]

class Splash(base.Base):
    def __init__(self, parent):
        super(Splash, self).__init__(parent)
        utils_path = os.path.join(BlenderVR_root, 'utils')
        font_path = os.path.join(utils_path, 'font.ttf')
        self._font_id = blf.load(font_path)
        self._ecg_values = ECG_VALUES
        self._message = ''
        self._ecg_values_size = len(self._ecg_values)
        self._repeat = 8
        self._total_size = self._ecg_values_size * self._repeat
        self._extinction = 3.0

        self._official_splash = (bge.logic.getCurrentScene().name ==
                                                "BlenderVR Splash Screen")

        if self._official_splash:
            return

        logo_path = os.path.join(utils_path, 'bvr-logo.ppm')
        logofile = open(logo_path, 'r')
        magic = logofile.readline().strip()
        if magic != 'P3': # check for plain ppm format
            self.logger.warning('Cannot load BlenderVR Logo (wrong .ppm format)')
            return
        comment = logofile.readline() # remove comment line (Gimp generated)
        assert comment    # avoid unused warning
        if not comment[0] == '#': # if generated file doesn't have this comment line (varies between e.g. Gimp and MagickImage)
            logoformat = comment
        else:
            logoformat = logofile.readline().strip().split(' ')
        highest = float(logofile.readline())
        texture_buffer = []
        while 1:
            line = logofile.readline().strip()
            try:
                value = [int(255 * (float(x) / highest)) for x in line.split(' ')]
            except ValueError:
                break
            texture_buffer.append(value)

        if type(texture_buffer[0]) is list:
            # from list of list to list (in line of values (per lines) scenario)
            texture_buffer = [item for sublist in texture_buffer for item in sublist]

        texture_buffer = Buffer(GL_BYTE, len(texture_buffer), texture_buffer)

        glEnable(GL_TEXTURE_2D)
        texture_id_buffer = Buffer(GL_INT, 1)
        glGenTextures(1, texture_id_buffer)
        self._texture_id = texture_id_buffer[0]
        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, int(logoformat[0]),
                    int(logoformat[1]), 0, GL_RGB, GL_UNSIGNED_BYTE,
                    texture_buffer)
        glDisable(GL_TEXTURE_2D)

    def setMessage(self, message):
        self._message = message

    def sceneIsSplash(self):
        return self._official_splash

    def isRunning(self):
        return self._run in bge.logic.getCurrentScene().post_draw

    def start(self):
        if not self.isRunning():
            self._first_time = int(self._ecg_values_size * time.time())
            bge.logic.getCurrentScene().post_draw.append(self._run)

    def stop(self):
        if self.isRunning():
            bge.logic.getCurrentScene().post_draw.remove(self._run)

    def _draw_text(self, text, line):
        blf.size(self._font_id, 100, 100)
        dimensions = blf.dimensions(self._font_id, text)
        scale = 90 * self._width / dimensions[0]
        blf.size(self._font_id, 100, int(scale))
        blf.position(self._font_id, 0.05 * self._width,
                                        (line + 1) * self._height / 6.0, 0)
        blf.draw(self._font_id, text)

    def _draw_ecg(self, index, width, shift):
        index %= self._total_size
        glVertex2f(shift + width * index / self._total_size,
                   self._height * self._ecg_values[
                                   int(index) % self._ecg_values_size] / 12.0)

    def _run(self):
        self._width = bge.render.getWindowWidth()
        self._height = bge.render.getWindowHeight()

        if not self._official_splash:
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT
                    | GL_STENCIL_BUFFER_BIT)
        glDisable(GL_BLEND)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_TEXTURE_1D)
        glDisable(GL_TEXTURE_2D)

        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(0, self._width, 0, self._height)

        if not self._official_splash:
            if self._width > self._height:
                square_size = self._height / 2.1
            else:
                square_size = self._width / 2.1

            glColor4f(1.0, 1.0, 1.0, 1.0)

            if hasattr(self, '_texture_id'):
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self._texture_id)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                                                                GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                                                GL_NEAREST)

                x1 = self._width / 2.0 - square_size / 2.0
                y1 = self._height / 2.0
                x2 = self._width / 2.0 + square_size / 2.0
                y2 = self._height / 2.0 + square_size

                glBegin(GL_QUADS)
                glTexCoord2f(0, 1)
                glVertex2f(x1, y1)

                glTexCoord2f(0, 0)
                glVertex2f(x1, y2)

                glTexCoord2f(1, 0)
                glVertex2f(x2, y2)

                glTexCoord2f(1, 1)
                glVertex2f(x2, y1)

                glEnd()

                glDisable(GL_TEXTURE_2D)
            else:
                glColor4f(0.8, 0.25, 0.0, 1.0)
                self._draw_text("BlenderVR", 3)

        # BLF drawing routine
        glColor4f(0.6, 0.6, 0.6, 1.0)
        self._draw_text(self._message, 1)

        line_width = 10.0
        assert line_width    # avoid assigned but never used
        width = 0.9 * self._width
        shift = 0.05 * self._width
        glLineWidth(1.0)

        window = int(self._extinction * self._ecg_values_size)
        start = int(self._ecg_values_size * time.time()) - self._first_time
        end = start + window
        for index in range(start, end):
            if ((index + 1) % self._total_size) != 0:
                attenuation = (index - start) / window

                glLineWidth(4.0 * attenuation)
                glColor4f(0.7 * attenuation, 0.7 * attenuation, 0.7 * attenuation, 1.0)
                glBegin(GL_LINES)
                self._draw_ecg(index, width, shift)
                self._draw_ecg(index + 1, width, shift)
                glEnd()

        glColor4f(0.7, 0.7, 0.7, 1.0)
        glPointSize(7.0)
        glBegin(GL_POINTS)
        self._draw_ecg(index, width, shift)
        glEnd()
