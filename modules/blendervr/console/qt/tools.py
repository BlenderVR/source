#!/usr/bin/env python3.2

from ...tools.gui.qt import QtGui, QtCore

class MessagesColors:
    def __init__(self):
        self._colors  = {}
        for name, value in {'default'  : ((255, 255, 255), (0, 0, 0)),
                            'DEBUG'    : ((255, 255, 255), (0, 90, 0)),
                            'INFO'     : ((255, 255, 255), (0, 0, 0)),
                            'WARNING'  : ((255, 255, 255), (0,0,164)),
                            'ERROR'    : ((255, 255, 255), (164,0,0)),
                            'CRITICAL' : ((154, 0, 0), (255, 255, 255)),
                            'stdout'   : ((230, 230, 230), (0, 0, 0)),
                            'stderr'   : ((230, 230, 230), (255, 0, 0))}.items():
            self._colors[name] = (QtGui.QColor(*(value[0])), QtGui.QColor(*(value[1])))

    def getColors(self, level):
        if level in self._colors:
            return self._colors[level]
        return None
