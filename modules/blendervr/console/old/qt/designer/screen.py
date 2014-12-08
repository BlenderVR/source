# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/damien/sources/blenderVR/trunk/modules/blendervr/console/qt/designer/screen.ui'
#
# Created: Mon Oct  6 13:53:39 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_screen(object):
    def setupUi(self, screen):
        screen.setObjectName(_fromUtf8("screen"))
        screen.resize(853, 634)
        self.gridLayout = QtGui.QGridLayout(screen)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.clear_log = QtGui.QPushButton(screen)
        self.clear_log.setObjectName(_fromUtf8("clear_log"))
        self.gridLayout.addWidget(self.clear_log, 0, 0, 1, 1)
        self.log_level_selector = QtGui.QComboBox(screen)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log_level_selector.sizePolicy().hasHeightForWidth())
        self.log_level_selector.setSizePolicy(sizePolicy)
        self.log_level_selector.setObjectName(_fromUtf8("log_level_selector"))
        self.gridLayout.addWidget(self.log_level_selector, 0, 1, 1, 1)
        self.std_out = QtGui.QPushButton(screen)
        self.std_out.setCheckable(True)
        self.std_out.setObjectName(_fromUtf8("std_out"))
        self.gridLayout.addWidget(self.std_out, 0, 2, 1, 1)
        self.std_err = QtGui.QPushButton(screen)
        self.std_err.setCheckable(True)
        self.std_err.setObjectName(_fromUtf8("std_err"))
        self.gridLayout.addWidget(self.std_err, 0, 3, 1, 1)
        self.log_window = QtGui.QTextEdit(screen)
        self.log_window.setReadOnly(True)
        self.log_window.setObjectName(_fromUtf8("log_window"))
        self.gridLayout.addWidget(self.log_window, 1, 0, 1, 4)

        self.retranslateUi(screen)
        QtCore.QObject.connect(self.clear_log, QtCore.SIGNAL(_fromUtf8("clicked()")), self.log_window.clear)
        QtCore.QMetaObject.connectSlotsByName(screen)

    def retranslateUi(self, screen):
        screen.setWindowTitle(QtGui.QApplication.translate("screen", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_log.setText(QtGui.QApplication.translate("screen", "clear", None, QtGui.QApplication.UnicodeUTF8))
        self.std_out.setText(QtGui.QApplication.translate("screen", "Standard output", None, QtGui.QApplication.UnicodeUTF8))
        self.std_err.setText(QtGui.QApplication.translate("screen", "Error output", None, QtGui.QApplication.UnicodeUTF8))


class screen(QtGui.QWidget, Ui_screen):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)

        self.setupUi(self)

