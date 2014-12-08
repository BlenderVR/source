# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/damien/sources/blenderVR/trunk/modules/blendervr/console/qt/designer/options.ui'
#
# Created: Mon Oct  6 13:53:38 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 300)
        self.gridLayout_2 = QtGui.QGridLayout(Form)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.debug_tab = QtGui.QWidget()
        self.debug_tab.setObjectName(_fromUtf8("debug_tab"))
        self.gridLayout = QtGui.QGridLayout(self.debug_tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.debug_daemon = QtGui.QCheckBox(self.debug_tab)
        self.debug_daemon.setObjectName(_fromUtf8("debug_daemon"))
        self.gridLayout.addWidget(self.debug_daemon, 2, 0, 1, 1)
        self.restart_daemons = QtGui.QPushButton(self.debug_tab)
        self.restart_daemons.setObjectName(_fromUtf8("restart_daemons"))
        self.gridLayout.addWidget(self.restart_daemons, 2, 1, 1, 1)
        self.executables = QtGui.QCheckBox(self.debug_tab)
        self.executables.setObjectName(_fromUtf8("executables"))
        self.gridLayout.addWidget(self.executables, 3, 0, 1, 1)
        self.reload_processor = QtGui.QPushButton(self.debug_tab)
        self.reload_processor.setObjectName(_fromUtf8("reload_processor"))
        self.gridLayout.addWidget(self.reload_processor, 0, 1, 1, 1)
        self.debug_processor = QtGui.QCheckBox(self.debug_tab)
        self.debug_processor.setObjectName(_fromUtf8("debug_processor"))
        self.gridLayout.addWidget(self.debug_processor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.debug_tab, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.debug_daemon.setText(QtGui.QApplication.translate("Form", "Daemon", None, QtGui.QApplication.UnicodeUTF8))
        self.restart_daemons.setText(QtGui.QApplication.translate("Form", "Restart", None, QtGui.QApplication.UnicodeUTF8))
        self.executables.setText(QtGui.QApplication.translate("Form", "Display executable files", None, QtGui.QApplication.UnicodeUTF8))
        self.reload_processor.setText(QtGui.QApplication.translate("Form", "Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.debug_processor.setText(QtGui.QApplication.translate("Form", "Processor", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.debug_tab), QtGui.QApplication.translate("Form", "Debug", None, QtGui.QApplication.UnicodeUTF8))


class Form(QtGui.QWidget, Ui_Form):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)

        self.setupUi(self)

