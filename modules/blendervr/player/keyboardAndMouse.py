# -*- coding: utf-8 -*-
# file: blendervr/player/keyboardAndMouse.py

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

import bge
import copy
import datetime
import math
from . import device

MOUSE_POSITION = 'mouse position'
BUTTON_LEFT = 'mouse left button'
BUTTON_MIDDLE = 'mouse middle button'
BUTTON_RIGHT = 'mouse right button'
WHEEL_UP = 'mouse wheel up'
WHEEL_DOWN = 'mouse wheel down'

WIDTH = 'width'
HEIGHT = 'height'


class KeyboardAndMouse(device.Sender):
    def __init__(self, parent):
        super(KeyboardAndMouse, self).__init__(parent,
                                {'processor_method': 'keyboardAndMouse'})
        # Backup the data
        # self._keyboard = copy.copy(bge.logic.keyboard.events)
        # active_events = bge.logic.keyboard.active_events
        # self.logger.debug('keyboard',self._keyboard)
        # self.logger.debug('active',active_events)
        self._mouse_events = None
        self._mouse_position = None
        self._screen = None

    def getScreen():
        return {WIDTH: bge.render.getWindowWidth(),
                HEIGHT: bge.render.getWindowHeight()}

    def start(self):
        return

    def _getState(state):
        if state == bge.logic.KX_INPUT_NONE:
            return device.STATE_FREE
        if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
            return device.STATE_PRESS
        if state == bge.logic.KX_INPUT_ACTIVE:
            return device.STATE_ACTIVE
        if state == bge.logic.KX_INPUT_JUST_RELEASED:
            return device.STATE_RELEASE
        return device.STATE_FREE

    def run(self):
        now = datetime.datetime.now()

        # Processing of the screen width and heght
        screen = KeyboardAndMouse.getScreen()
        if self._screen != screen:
            self._screen = copy.copy(screen)
            self.process(screen)

        # Processing keyboard !
        active_events = bge.logic.keyboard.active_events
        if active_events:
            for key in active_events.keys():
                    info = {'key': key,
                            'state': KeyboardAndMouse._getState(active_events[key]),
                            'time': now}
                    self.process(info)

        # Processing mouse !
        mouse_events = bge.logic.mouse.events
        mouse_position = (math.floor(bge.logic.mouse.position[0]
                                * self._screen[WIDTH]),
                          math.floor(bge.logic.mouse.position[1]
                                * self._screen[HEIGHT]))
        if (self._mouse_position != mouse_position) \
                                or (self._mouse_events != mouse_events):
            self._mouse_events = copy.copy(mouse_events)
            self._mouse_position = copy.copy(mouse_position)

            info = {MOUSE_POSITION: mouse_position,
                    'time': now
                    }
            infoidentmap = {BUTTON_LEFT: bge.events.LEFTMOUSE,
                            BUTTON_MIDDLE: bge.events.MIDDLEMOUSE,
                            BUTTON_RIGHT: bge.events.RIGHTMOUSE,
                            WHEEL_UP: bge.events.WHEELUPMOUSE,
                            WHEEL_DOWN: bge.events.WHEELDOWNMOUSE}
            for name, bge_name in infoidentmap.items():
                info[name] = KeyboardAndMouse._getState(mouse_events[bge_name])
            self.process(info)

