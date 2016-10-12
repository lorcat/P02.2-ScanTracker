# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_hideable.ui'
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

class Ui_hider(object):
    def setupUi(self, hider):
        hider.setObjectName(_fromUtf8("hider"))
        hider.resize(516, 62)
        hider.setToolTip(_fromUtf8(""))
        hider.setStyleSheet(_fromUtf8(""))
        self.gridLayout = QtGui.QGridLayout(hider)
        self.gridLayout.setMargin(5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hide_button = QtGui.QToolButton(hider)
        self.hide_button.setMinimumSize(QtCore.QSize(25, 25))
        self.hide_button.setMaximumSize(QtCore.QSize(25, 25))
        self.hide_button.setStyleSheet(_fromUtf8(""))
        self.hide_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/images/ic_remove_red_eye_grey600_36dp.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/images/ic_remove_red_eye_black_36dp.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.hide_button.setIcon(icon)
        self.hide_button.setIconSize(QtCore.QSize(20, 20))
        self.hide_button.setCheckable(True)
        self.hide_button.setChecked(True)
        self.hide_button.setObjectName(_fromUtf8("hide_button"))
        self.gridLayout.addWidget(self.hide_button, 0, 0, 1, 1)
        self.hideable_label = QtGui.QLabel(hider)
        self.hideable_label.setText(_fromUtf8(""))
        self.hideable_label.setObjectName(_fromUtf8("hideable_label"))
        self.gridLayout.addWidget(self.hideable_label, 0, 1, 1, 1)
        self.hideable = QtGui.QWidget(hider)
        self.hideable.setMaximumSize(QtCore.QSize(16777215, 300))
        self.hideable.setObjectName(_fromUtf8("hideable"))
        self.hideable_layout = QtGui.QGridLayout(self.hideable)
        self.hideable_layout.setMargin(0)
        self.hideable_layout.setObjectName(_fromUtf8("hideable_layout"))
        self.gridLayout.addWidget(self.hideable, 1, 0, 1, 2)

        self.retranslateUi(hider)
        QtCore.QObject.connect(self.hide_button, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.hideable.setVisible)
        QtCore.QMetaObject.connectSlotsByName(hider)

    def retranslateUi(self, hider):
        hider.setWindowTitle(QtGui.QApplication.translate("hider", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.hide_button.setToolTip(QtGui.QApplication.translate("hider", "Show/Hide", None, QtGui.QApplication.UnicodeUTF8))

import resource_hider_rc
