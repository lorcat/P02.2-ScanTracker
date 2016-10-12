# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_scanwindow.ui'
#
# Created: Thu May 28 17:53:51 2015
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_scanWindow(object):
    def setupUi(self, scanWindow):
        scanWindow.setObjectName(_fromUtf8("scanWindow"))
        scanWindow.resize(777, 719)
        self.gridLayout = QtGui.QGridLayout(scanWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(scanWindow)
        self.splitter.setBaseSize(QtCore.QSize(0, 0))
        self.splitter.setLineWidth(3)
        self.splitter.setMidLineWidth(10)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tool_selector = QtGui.QToolBox(self.splitter)
        self.tool_selector.setObjectName(_fromUtf8("tool_selector"))
        self.page_scans = QtGui.QWidget()
        self.page_scans.setGeometry(QtCore.QRect(0, 0, 692, 645))
        self.page_scans.setObjectName(_fromUtf8("page_scans"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_scans)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.widget = QtGui.QWidget(self.page_scans)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_5 = QtGui.QGridLayout(self.widget)
        self.gridLayout_5.setMargin(0)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.cb_latest = QtGui.QCheckBox(self.widget)
        self.cb_latest.setObjectName(_fromUtf8("cb_latest"))
        self.gridLayout_5.addWidget(self.cb_latest, 0, 0, 1, 1)
        self.cb_derivative = QtGui.QCheckBox(self.widget)
        self.cb_derivative.setObjectName(_fromUtf8("cb_derivative"))
        self.gridLayout_5.addWidget(self.cb_derivative, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem, 0, 4, 1, 1)
        self.cb_invert = QtGui.QCheckBox(self.widget)
        self.cb_invert.setObjectName(_fromUtf8("cb_invert"))
        self.gridLayout_5.addWidget(self.cb_invert, 0, 3, 1, 1)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)
        self.tool_selector.addItem(self.page_scans, _fromUtf8(""))
        self.page_channels = QtGui.QWidget()
        self.page_channels.setGeometry(QtCore.QRect(0, 0, 692, 645))
        self.page_channels.setObjectName(_fromUtf8("page_channels"))
        self.gridLayout_3 = QtGui.QGridLayout(self.page_channels)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tool_selector.addItem(self.page_channels, _fromUtf8(""))
        self.widget_graph = QtGui.QWidget(self.splitter)
        self.widget_graph.setObjectName(_fromUtf8("widget_graph"))
        self.gridLayout_4 = QtGui.QGridLayout(self.widget_graph)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(scanWindow)
        self.tool_selector.setCurrentIndex(0)
        QtCore.QObject.connect(self.cb_derivative, QtCore.SIGNAL(_fromUtf8("clicked()")), scanWindow.actionApplyDerivative)
        QtCore.QObject.connect(self.cb_invert, QtCore.SIGNAL(_fromUtf8("clicked()")), scanWindow.actionApplyInversion)
        QtCore.QMetaObject.connectSlotsByName(scanWindow)

    def retranslateUi(self, scanWindow):
        scanWindow.setWindowTitle(QtGui.QApplication.translate("scanWindow", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_latest.setToolTip(QtGui.QApplication.translate("scanWindow", "Always jump to the latest scan", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_latest.setText(QtGui.QApplication.translate("scanWindow", "track latest", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_derivative.setToolTip(QtGui.QApplication.translate("scanWindow", "Calculate Derivative", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_derivative.setText(QtGui.QApplication.translate("scanWindow", "d\'", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_invert.setToolTip(QtGui.QApplication.translate("scanWindow", "Invert current data", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_invert.setText(QtGui.QApplication.translate("scanWindow", "inv.", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_selector.setItemText(self.tool_selector.indexOf(self.page_scans), QtGui.QApplication.translate("scanWindow", "Scans:", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_selector.setItemText(self.tool_selector.indexOf(self.page_channels), QtGui.QApplication.translate("scanWindow", "Channels:", None, QtGui.QApplication.UnicodeUTF8))

