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

from ..gui.logger import Logger as common_Logger
from ...tools.gui.qt import QtGui, QtCore

class Logger(common_Logger):

    def __init__(self, parent, config_index, window, log_level_selector):
        common_Logger.__init__(self, parent, config_index)
        self._window = window
        self._log_level_selector = log_level_selector

        self._log_level_selector.currentIndexChanged.connect(self.cb_set_log_level)

        from . import tools
        self._logger_colors = tools.MessagesColors()

        all_log_levels = self.logger.getVerbosities()
        current_log_level = self.profile.getValue(self._level_config_index) 
        self._log_level_selector.clear()
        for verbosity in all_log_levels:
            self._log_level_selector.addItem(verbosity)
        if current_log_level in all_log_levels:
            self._log_level_selector.setCurrentIndex(all_log_levels.index(current_log_level))

    def cb_set_log_level(self):
        all_log_levels = self.logger.getVerbosities()
        common_Logger.set_log_level(self, all_log_levels[self._log_level_selector.currentIndex()])

    def _append_to_window(self, message, level = None):
        try:
            color = self._logger_colors.getColors(level)
            if color is None:
                color = self._logger_colors.getColors('default')
            self._window.setTextBackgroundColor(color[0])
            self._window.setTextColor(color[1])
            self._window.insertPlainText(message + "\n")
            scroll_bar = self._window.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
        except RuntimeError:
            # I can't find where this print is done ... :-(
            pass

    def clear(self):
        self._window.clear()
