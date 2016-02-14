# -*- coding: utf-8 -*-
# file: blendervr/console/qt/console.py

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

from ...tools.gui.qt import QtGui, QtCore, Common
from ..gui.console import GUI as common_GUI
import os
from ... import version
from . import options


class MainWindow(Common, QtGui.QMainWindow):
    def __init__(self, owner, profile, profile_indices):
        QtGui.QMainWindow.__init__(self)
        Common.__init__(self, owner, profile, profile_indices)


class GUI(common_GUI):
    def __init__(self):
        common_GUI.__init__(self)

        self._window = MainWindow(self, self.profile,
                                {'window geometry': ['windows', 'main']})

        # Set up the user interface from Designer.
        from ...tools import gui, getModulePath
        self._console_ui = gui.load("/".join((getModulePath(), 'designer',
                                            'console.ui')), self._window)

        self._window.destroyed.connect(self.cb_close)
        self._console_ui.menuQuit.triggered.connect(self.cb_close)
        self._console_ui.main_tab.currentChanged.connect(
                                        self.cb_set_current_tab)
        self._console_ui.configuration_file.clicked.connect(
                                        self.cb_set_configuration_file)
        self._console_ui.add_configuration_path.clicked.connect(
                                        self.cb_add_configuration_path)
        self._console_ui.remove_configuration_path.clicked.connect(
                                        self.cb_remove_configuration_path)
        self._console_ui.load_configuration_file.clicked.connect(
                                        self.cb_load_configuration_file)
        self._console_ui.blender_file.clicked.connect(self.cb_set_blender_file)
        self._console_ui.processor_file.clicked.connect(
                                        self.cb_set_processor_file)
        self._console_ui.link_processor_to_blender.toggled.connect(
                                        self.cb_set_link_processor_to_blender)
        self._console_ui.set_screen_set.clicked.connect(self.cb_set_screen_set)
        self._console_ui.select_screen_set.currentIndexChanged.connect(self.cb_set_screen_set)
        self._console_ui.menuProcessor.triggered.connect(
                                        self.cb_processor_window)

        self._console_ui.start.clicked.connect(self.cb_start)
        self._console_ui.stop.clicked.connect(self.cb_stop)

        from . import logger
        self._logger_window = logger.Logger(self, ['log'],
                                            self._console_ui.log_window,
                                            self._console_ui.log_level_selector)

        self._window.setWindowTitle('BlenderVR (v' + str(version) + ')')
        self._options = options.GUI(self)

        self._console_ui.menuWindows.addAction(self._options.getMenu())

    def getWindow(self):
        return self._window

    def start(self):
        self._screens._setScreensMenu(self._console_ui.menuScreens)
        common_GUI.start(self)
        self._window.start()
        self._options.start()

        for QT_name, index in {'configuration_file': ['config', 'file'],
                           'blender_file': ['files', 'blender'],
                           'processor_file': ['files', 'processor']}.items():
            _value = self.profile.getValue(index)
            if _value:
                getattr(self._console_ui, QT_name).setText(_value)

        self._console_ui.link_processor_to_blender.setChecked(
                                    self.profile.getValue(['files', 'link']))

        for path in self._get_configuration_paths_list():
            item = QtGui.QListWidgetItem()
            self._console_ui.configuration_paths.addItem(item)
            item.setText(path)

        current_tab = self.profile.getValue(['current_tab'])
        if current_tab is not None:
            self._console_ui.main_tab.setCurrentIndex(current_tab)

        self._console_ui.menuProcessor.setChecked(
                            self.profile.getValue(['processor', 'toggle']))

        self._window.show()

    def quit(self):
        common_GUI.quit(self)
        try:
            self._processor.quit()
        except:
            pass

    def main(self):
        global qt_application
        return_value = qt_application.exec_()

    def addTimeout(self, time, callback):
        timer = QtCore.QTimer()
        timer.timeout.connect(callback)
        timer.setSingleShot(True)
        timer.start(time)
        return timer

    def addListenTo(self, socket, callback, data=None):
        notifier = QtCore.QSocketNotifier(
                                socket, QtCore.QSocketNotifier.Read, data)
        notifier.activated.connect(callback)
        return notifier

    def removeListenTo(self, tag):
        del(tag)

    def cb_set_current_tab(self):
        self.profile.setValue(['current_tab'],
                            self._console_ui.main_tab.currentIndex())

    def cb_set_configuration_file(self):
        previous_file = self.profile.getValue(['config', 'file'])
        if previous_file:
            previous_file = os.path.dirname(previous_file)
        else:
            previous_file = ''
        file_name = QtGui.QFileDialog.getOpenFileName(self._window,
                "Open Configuration file", previous_file, "XML file (*.xml)")
        if isinstance(file_name, tuple):
            file_name = file_name[0]
        if file_name:
            self._console_ui.configuration_file.setText(file_name)
            self.cb_load_configuration_file()

    def _get_configuration_paths_list(self):
        paths = self.profile.getValue(['config', 'path'])
        if isinstance(paths, str):
            return [paths]
        if isinstance(paths, list):
            return paths
        return []

    def cb_update_liste_paths(self, *args):
        paths = []
        for index in range(0, self._paths_model.rowCount()):
            index = self._paths_model.index(index, 0)
            data = self._paths_model.itemData(index)
            paths.append(data[0])
        self.profile.setValue(['config', 'path'], paths)

    def cb_remove_configuration_path(self, *args):
        paths_widget = self._console_ui.configuration_paths
        items = paths_widget.selectedItems()
        for item in items:
            paths_widget.takeItem(paths_widget.row(item))

    def cb_add_configuration_path(self):
        directory_name = QtGui.QFileDialog.getExistingDirectory(self._window)
        confpaths = self._console_ui.configuration_paths
        if directory_name and (len(confpaths.findItems(directory_name,
                                        QtCore.Qt.MatchExactly)) == 0):
            item = QtGui.QListWidgetItem()
            item.setText(directory_name)
            self._console_ui.configuration_paths.addItem(item)

    def cb_load_configuration_file(self):
        configuration_file = self._console_ui.configuration_file.text()
        self.profile.setValue(['config', 'file'], configuration_file)
        paths = []
        for index in range(0, self._console_ui.configuration_paths.count()):
            item = self._console_ui.configuration_paths.item(index)
            paths.append(item.text())
        self.profile.setValue(['config', 'path'], paths)
        self.load_configuration_file()

    def display_screen_sets(self, screenSets):
        self._console_ui.select_screen_set.clear()
        for screenScet in screenSets:
            self._console_ui.select_screen_set.addItem(screenScet)
        currentScreenSet = self.profile.getValue(['screen', 'set'])
        if currentScreenSet in screenSets:
            self._console_ui.select_screen_set.setCurrentIndex(
                                    screenSets.index(currentScreenSet))
            self._console_ui.current_screen_set.setText(currentScreenSet)

    def cb_set_screen_set(self):
        if hasattr(self, '_first_time_cb_set_screen_set'):
            # to avoid resetting screen set to default (first in list) at console opening,
            # thus remembering selected screenset at last console close, related to the line in __init__:
            # --> self._console_ui.select_screen_set.currentIndexChanged.connect(self.cb_set_screen_set)
            all_screen_sets = self._possibleScreenSets
            current = all_screen_sets[
                            self._console_ui.select_screen_set.currentIndex()]
            self.profile.setValue(['screen', 'set'], current)
            self._console_ui.current_screen_set.setText(current)
            self.set_screen_set()
        else:
            self._first_time_cb_set_screen_set = True

    def cb_set_blender_file(self):
        previous_file = self.profile.getValue(['files', 'blender'])
        if previous_file:
            previous_file = os.path.dirname(previous_file)
        else:
            previous_file = ''
        file_name = QtGui.QFileDialog.getOpenFileName(self._window,
                        "Open Blender file", previous_file,
                        "blender file (*.blend)")
        if isinstance(file_name, tuple):
            file_name = file_name[0]
        if file_name:
            self.profile.setValue(['files', 'blender'], file_name)
            self._console_ui.blender_file.setText(file_name)
            self._linkProcessorToBlenderFile()

    def cb_set_processor_file(self):
        previous_file = self.profile.getValue(['files', 'processor'])
        if previous_file:
            previous_file = os.path.dirname(previous_file)
        else:
            previous_file = ''
        file_name = QtGui.QFileDialog.getOpenFileName(self._window,
                        "Open Processor file", previous_file,
                        "processor file (*.processor.py)")
        if isinstance(file_name, tuple):
            file_name = file_name[0]
        if file_name:
            self.profile.setValue(['files', 'processor'], file_name)
            self._console_ui.processor_file.setText(file_name)
            self._linkProcessorToBlenderFile()

    def _force_processor_file(self, processor_file_name):
        self._console_ui.processor_file.setText(processor_file_name + ' ...')

    def cb_set_link_processor_to_blender(self):
        if self._window.isVisible():
            self.profile.setValue(['files', 'link'],
                    self._console_ui.link_processor_to_blender.isChecked())
            self._linkProcessorToBlenderFile()

    def updateStatus(self, message, state=None):
        self._console_ui.status_bar.showMessage(message)

    def _display_status(self, state, states):
        self._options.BlenderVR_state_changed(False)
        if state == 'stopped':
            label_content = 'stopped'
            background = QtGui.QColor(127, 0, 0)
            self._console_ui.stop.setEnabled(False)
            self._console_ui.start.setEnabled(True)
            self._options.BlenderVR_state_changed(True)
        elif state == 'starting':
            label_content = 'starting'
            background = QtGui.QColor(255, 127, 0)
            self._console_ui.stop.setEnabled(True)
            self._console_ui.start.setEnabled(False)
        elif state == 'running':
            label_content = 'running'
            background = QtGui.QColor(0, 127, 0)
            self._console_ui.stop.setEnabled(True)
            self._console_ui.start.setEnabled(False)
        else:
            label_content = 'Transition or error'
            background = QtGui.QColor(127, 127, 127)
            self._console_ui.stop.setEnabled(True)
            self._console_ui.start.setEnabled(False)

        for state_name, number in states.items():
            getattr(self._console_ui, 'nb_' + state_name).setText(str(number))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(background)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,
                                            QtGui.QPalette.WindowText, brush)
        self._console_ui.status.setPalette(palette)
        self._console_ui.status.setText(label_content)

    def cb_start(self):
        self.start_simulation()

    def cb_stop(self):
        self.stop_simulation()

    def cb_close(self):
        self.quit()

    def cb_processor_window(self):
        self.profile.setValue(['processor', 'toggle'],
                             self._console_ui.menuProcessor.isChecked())
        self.update_processor()

    def update_processor(self):
        if self._processor:
            if self._previous_state != 'running':
                self._processor.hide()
                return
            if self.profile.getValue(['processor', 'toggle']):
                self._processor.show()
            else:
                self._processor.hide()

def quit():
    QtCore.QCoreApplication.exit()

import sys
qt_application = QtGui.QApplication(sys.argv)
