# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_quickmotor.ui'
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

class Ui_quickmotor(object):
    def setupUi(self, quickmotor):
        quickmotor.setObjectName(_fromUtf8("quickmotor"))
        quickmotor.resize(902, 102)
        quickmotor.setMinimumSize(QtCore.QSize(0, 100))
        quickmotor.setMaximumSize(QtCore.QSize(16777215, 102))
        self.gridLayout_3 = QtGui.QGridLayout(quickmotor)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.stacked_motor = QtGui.QStackedWidget(quickmotor)
        self.stacked_motor.setObjectName(_fromUtf8("stacked_motor"))
        self.page_nomotor = QtGui.QWidget()
        self.page_nomotor.setObjectName(_fromUtf8("page_nomotor"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_nomotor)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.page_nomotor)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.stacked_motor.addWidget(self.page_nomotor)
        self.page_motor = QtGui.QWidget()
        self.page_motor.setObjectName(_fromUtf8("page_motor"))
        self.gridLayout_4 = QtGui.QGridLayout(self.page_motor)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.motor_state = TaurusLed(self.page_motor)
        self.motor_state.setMinimumSize(QtCore.QSize(30, 30))
        self.motor_state.setMaximumSize(QtCore.QSize(30, 16777215))
        self.motor_state.setObjectName(_fromUtf8("motor_state"))
        self.gridLayout_4.addWidget(self.motor_state, 0, 0, 1, 1)
        self.motor_name = QtGui.QLabel(self.page_motor)
        self.motor_name.setMinimumSize(QtCore.QSize(90, 30))
        self.motor_name.setMaximumSize(QtCore.QSize(16777215, 30))
        self.motor_name.setObjectName(_fromUtf8("motor_name"))
        self.gridLayout_4.addWidget(self.motor_name, 0, 1, 1, 1)
        self.motor_label = TaurusLabel(self.page_motor)
        self.motor_label.setMinimumSize(QtCore.QSize(130, 30))
        self.motor_label.setMaximumSize(QtCore.QSize(100, 30))
        self.motor_label.setStyleSheet(_fromUtf8("QWidget {font-size: 14px; font-weight: bold;}"))
        self.motor_label.setUseParentModel(False)
        self.motor_label.setObjectName(_fromUtf8("motor_label"))
        self.gridLayout_4.addWidget(self.motor_label, 0, 2, 1, 1)
        self.motor_edit = TaurusValueLineEdit(self.page_motor)
        self.motor_edit.setMinimumSize(QtCore.QSize(130, 30))
        self.motor_edit.setMaximumSize(QtCore.QSize(150, 30))
        self.motor_edit.setStyleSheet(_fromUtf8("TaurusValueLineEdit {color: black; font-weight: bold; font-size: 14px;}"))
        self.motor_edit.setObjectName(_fromUtf8("motor_edit"))
        self.gridLayout_4.addWidget(self.motor_edit, 0, 3, 1, 1)
        self.label = QtGui.QLabel(self.page_motor)
        self.label.setMinimumSize(QtCore.QSize(5, 30))
        self.label.setMaximumSize(QtCore.QSize(5, 30))
        self.label.setStyleSheet(_fromUtf8("QLabel {background-color: #777;}"))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 0, 4, 1, 1)
        self.label_initial = QtGui.QLabel(self.page_motor)
        self.label_initial.setStyleSheet(_fromUtf8("QLabel{font-size:20; font-weight: bold;}"))
        self.label_initial.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_initial.setObjectName(_fromUtf8("label_initial"))
        self.gridLayout_4.addWidget(self.label_initial, 0, 5, 1, 1)
        self.cmb_position = QtGui.QComboBox(self.page_motor)
        self.cmb_position.setMinimumSize(QtCore.QSize(150, 30))
        self.cmb_position.setMaximumSize(QtCore.QSize(200, 30))
        self.cmb_position.setStyleSheet(_fromUtf8("QWidget {font-size: 14px;}"))
        self.cmb_position.setObjectName(_fromUtf8("cmb_position"))
        self.gridLayout_4.addWidget(self.cmb_position, 0, 6, 1, 1)
        self.btn_position = QtGui.QPushButton(self.page_motor)
        self.btn_position.setMinimumSize(QtCore.QSize(0, 27))
        self.btn_position.setMaximumSize(QtCore.QSize(60, 27))
        self.btn_position.setObjectName(_fromUtf8("btn_position"))
        self.gridLayout_4.addWidget(self.btn_position, 0, 7, 1, 1)
        self.btn_center = QtGui.QPushButton(self.page_motor)
        self.btn_center.setMinimumSize(QtCore.QSize(0, 27))
        self.btn_center.setMaximumSize(QtCore.QSize(50, 16777215))
        self.btn_center.setObjectName(_fromUtf8("btn_center"))
        self.gridLayout_4.addWidget(self.btn_center, 0, 8, 1, 1)
        spacerItem = QtGui.QSpacerItem(13, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 9, 1, 1)
        self.label_4 = QtGui.QLabel(self.page_motor)
        self.label_4.setMinimumSize(QtCore.QSize(5, 30))
        self.label_4.setMaximumSize(QtCore.QSize(5, 30))
        self.label_4.setStyleSheet(_fromUtf8("QLabel {background-color: #777;}"))
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_4.addWidget(self.label_4, 1, 4, 1, 1)
        self.widget = QtGui.QWidget(self.page_motor)
        self.widget.setMinimumSize(QtCore.QSize(0, 35))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(5)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setStyleSheet(_fromUtf8("QLabel{font-size:20; font-weight: bold;}"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.pos_distance = QtGui.QLabel(self.widget)
        self.pos_distance.setMinimumSize(QtCore.QSize(100, 25))
        self.pos_distance.setStyleSheet(_fromUtf8("QLabel{background-color: #eee; border: 0px; font-size:20; color: #a0a0a0; font-weight: bold;}"))
        self.pos_distance.setText(_fromUtf8(""))
        self.pos_distance.setAlignment(QtCore.Qt.AlignCenter)
        self.pos_distance.setObjectName(_fromUtf8("pos_distance"))
        self.gridLayout.addWidget(self.pos_distance, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setStyleSheet(_fromUtf8("QLabel{font-size:20; font-weight: bold;}"))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)
        self.pos_center = QtGui.QLineEdit(self.widget)
        self.pos_center.setMinimumSize(QtCore.QSize(100, 25))
        self.pos_center.setMaximumSize(QtCore.QSize(100, 25))
        self.pos_center.setStyleSheet(_fromUtf8("QLineEdit {background-color: #eee; border: 0px; font-size:20; color: #a0a0a0; font-weight: bold;}"))
        self.pos_center.setAlignment(QtCore.Qt.AlignCenter)
        self.pos_center.setReadOnly(True)
        self.pos_center.setObjectName(_fromUtf8("pos_center"))
        self.gridLayout.addWidget(self.pos_center, 0, 3, 1, 1)
        self.gridLayout_4.addWidget(self.widget, 1, 5, 1, 4)
        self.stacked_motor.addWidget(self.page_motor)
        self.gridLayout_3.addWidget(self.stacked_motor, 1, 0, 1, 1)

        self.retranslateUi(quickmotor)
        self.stacked_motor.setCurrentIndex(1)
        QtCore.QObject.connect(self.btn_position, QtCore.SIGNAL(_fromUtf8("clicked()")), quickmotor.forcePosition)
        QtCore.QObject.connect(self.btn_center, QtCore.SIGNAL(_fromUtf8("clicked()")), quickmotor.forceCenter)
        QtCore.QMetaObject.connectSlotsByName(quickmotor)
        quickmotor.setTabOrder(self.motor_edit, self.btn_position)

    def retranslateUi(self, quickmotor):
        quickmotor.setWindowTitle(QtGui.QApplication.translate("quickmotor", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("quickmotor", "No Valid Motor Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.motor_name.setToolTip(QtGui.QApplication.translate("quickmotor", "Motor name", None, QtGui.QApplication.UnicodeUTF8))
        self.motor_name.setText(QtGui.QApplication.translate("quickmotor", "Motor", None, QtGui.QApplication.UnicodeUTF8))
        self.motor_edit.setToolTip(QtGui.QApplication.translate("quickmotor", "Motor position", None, QtGui.QApplication.UnicodeUTF8))
        self.motor_edit.setText(QtGui.QApplication.translate("quickmotor", "112", None, QtGui.QApplication.UnicodeUTF8))
        self.label_initial.setText(QtGui.QApplication.translate("quickmotor", "  Position:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_position.setToolTip(QtGui.QApplication.translate("quickmotor", "Select a reference point to go", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_position.setToolTip(QtGui.QApplication.translate("quickmotor", "Go to the selected point", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_position.setText(QtGui.QApplication.translate("quickmotor", "GO", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_center.setToolTip(QtGui.QApplication.translate("quickmotor", "Go to the center between two last selected points", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_center.setText(QtGui.QApplication.translate("quickmotor", "CEN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("quickmotor", "  Distance:", None, QtGui.QApplication.UnicodeUTF8))
        self.pos_distance.setToolTip(QtGui.QApplication.translate("quickmotor", "Distance relative to the last selected point", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("quickmotor", "Center:", None, QtGui.QApplication.UnicodeUTF8))
        self.pos_center.setToolTip(QtGui.QApplication.translate("quickmotor", "Center position between last selected points", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.display import TaurusLabel, TaurusLed
from taurus.qt.qtgui.input import TaurusValueLineEdit
