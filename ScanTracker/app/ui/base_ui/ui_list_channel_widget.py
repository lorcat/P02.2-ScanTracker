# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_list_channel_widget.ui'
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

class Ui_list_channel_widget(object):
    def setupUi(self, list_channel_widget):
        list_channel_widget.setObjectName(_fromUtf8("list_channel_widget"))
        list_channel_widget.resize(285, 40)
        list_channel_widget.setMinimumSize(QtCore.QSize(0, 40))
        list_channel_widget.setMaximumSize(QtCore.QSize(16777215, 40))
        self.gridLayout = QtGui.QGridLayout(list_channel_widget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(list_channel_widget)
        self.label_2.setMinimumSize(QtCore.QSize(40, 20))
        self.label_2.setMaximumSize(QtCore.QSize(40, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.ch_x = QtGui.QCheckBox(list_channel_widget)
        self.ch_x.setMinimumSize(QtCore.QSize(20, 20))
        self.ch_x.setText(_fromUtf8(""))
        self.ch_x.setObjectName(_fromUtf8("ch_x"))
        self.gridLayout.addWidget(self.ch_x, 0, 1, 1, 1)
        self.ch_y = QtGui.QCheckBox(list_channel_widget)
        self.ch_y.setMinimumSize(QtCore.QSize(20, 20))
        self.ch_y.setText(_fromUtf8(""))
        self.ch_y.setObjectName(_fromUtf8("ch_y"))
        self.gridLayout.addWidget(self.ch_y, 0, 2, 1, 1)
        self.ch_norm = QtGui.QCheckBox(list_channel_widget)
        self.ch_norm.setMinimumSize(QtCore.QSize(20, 20))
        self.ch_norm.setText(_fromUtf8(""))
        self.ch_norm.setObjectName(_fromUtf8("ch_norm"))
        self.gridLayout.addWidget(self.ch_norm, 0, 3, 1, 1)
        self.lb_channel = QtGui.QLabel(list_channel_widget)
        self.lb_channel.setMinimumSize(QtCore.QSize(0, 20))
        self.lb_channel.setText(_fromUtf8(""))
        self.lb_channel.setObjectName(_fromUtf8("lb_channel"))
        self.gridLayout.addWidget(self.lb_channel, 0, 4, 1, 1)
        self.gridLayout.setColumnStretch(4, 50)

        self.retranslateUi(list_channel_widget)
        QtCore.QObject.connect(self.ch_x, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), list_channel_widget.actionSetX)
        QtCore.QObject.connect(self.ch_y, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), list_channel_widget.actionSetY)
        QtCore.QObject.connect(self.ch_norm, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), list_channel_widget.actionSetNorm)
        QtCore.QMetaObject.connectSlotsByName(list_channel_widget)

    def retranslateUi(self, list_channel_widget):
        list_channel_widget.setWindowTitle(QtGui.QApplication.translate("list_channel_widget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("list_channel_widget", "x,y,n:", None, QtGui.QApplication.UnicodeUTF8))

