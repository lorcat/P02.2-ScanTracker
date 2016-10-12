# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_trend_holder.ui'
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

class Ui_trend_holder(object):
    def setupUi(self, trend_holder):
        trend_holder.setObjectName(_fromUtf8("trend_holder"))
        trend_holder.resize(662, 300)
        self.gridLayout = QtGui.QGridLayout(trend_holder)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.stack = QtGui.QStackedWidget(trend_holder)
        self.stack.setObjectName(_fromUtf8("stack"))
        self.page_loading = QtGui.QWidget()
        self.page_loading.setObjectName(_fromUtf8("page_loading"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_loading)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.page_loading)
        self.label.setStyleSheet(_fromUtf8("QLabel {font-size: 20px; color: #a0a0a0;}"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.stack.addWidget(self.page_loading)
        self.page_plots = QtGui.QWidget()
        self.page_plots.setObjectName(_fromUtf8("page_plots"))
        self.gridLayout_3 = QtGui.QGridLayout(self.page_plots)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.stats = QtGui.QWidget(self.page_plots)
        self.stats.setObjectName(_fromUtf8("stats"))
        self.gridLayout_10 = QtGui.QGridLayout(self.stats)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 10)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.wdgt1 = QtGui.QWidget(self.stats)
        self.wdgt1.setStyleSheet(_fromUtf8("QWidget#wdgt1 {border: 2px solid #ccc; background-color: #f0f0f0;}\n"
"QLineEdit {border:0px; background-color: #f0f0f0;}"))
        self.wdgt1.setObjectName(_fromUtf8("wdgt1"))
        self.gridLayout_5 = QtGui.QGridLayout(self.wdgt1)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setContentsMargins(3, 4, 3, 4)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_2 = QtGui.QLabel(self.wdgt1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 1)
        self.stat_fwhm = QtGui.QLineEdit(self.wdgt1)
        self.stat_fwhm.setMinimumSize(QtCore.QSize(100, 0))
        self.stat_fwhm.setMaximumSize(QtCore.QSize(100, 16777215))
        self.stat_fwhm.setStyleSheet(_fromUtf8(""))
        self.stat_fwhm.setReadOnly(True)
        self.stat_fwhm.setObjectName(_fromUtf8("stat_fwhm"))
        self.gridLayout_5.addWidget(self.stat_fwhm, 0, 1, 1, 1)
        self.gridLayout_10.addWidget(self.wdgt1, 0, 0, 1, 1)
        self.wdgt2 = QtGui.QWidget(self.stats)
        self.wdgt2.setStyleSheet(_fromUtf8("QWidget#wdgt2 {border-bottom: 2px solid #ccc; background-color: #f0f0f0; border-top: 2px solid #ccc; border-right: 2px solid #ccc;}\n"
"QLineEdit {border:0px; background-color: #f0f0f0;}"))
        self.wdgt2.setObjectName(_fromUtf8("wdgt2"))
        self.gridLayout_6 = QtGui.QGridLayout(self.wdgt2)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setContentsMargins(3, 4, 3, 4)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.stat_center = QtGui.QLineEdit(self.wdgt2)
        self.stat_center.setMinimumSize(QtCore.QSize(100, 0))
        self.stat_center.setMaximumSize(QtCore.QSize(100, 16777215))
        self.stat_center.setStyleSheet(_fromUtf8(""))
        self.stat_center.setReadOnly(True)
        self.stat_center.setObjectName(_fromUtf8("stat_center"))
        self.gridLayout_6.addWidget(self.stat_center, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.wdgt2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_6.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayout_10.addWidget(self.wdgt2, 0, 1, 1, 1)
        self.wdgt3 = QtGui.QWidget(self.stats)
        self.wdgt3.setStyleSheet(_fromUtf8("QWidget#wdgt3 {border-bottom: 2px solid #ccc; background-color: #f0f0f0; border-top: 2px solid #ccc; border-right: 2px solid #ccc;}\n"
"QLineEdit {border:0px; background-color: #f0f0f0;}"))
        self.wdgt3.setObjectName(_fromUtf8("wdgt3"))
        self.gridLayout_9 = QtGui.QGridLayout(self.wdgt3)
        self.gridLayout_9.setSpacing(0)
        self.gridLayout_9.setContentsMargins(3, 4, 3, 4)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.stat_cms = QtGui.QLineEdit(self.wdgt3)
        self.stat_cms.setMinimumSize(QtCore.QSize(100, 0))
        self.stat_cms.setMaximumSize(QtCore.QSize(100, 16777215))
        self.stat_cms.setStyleSheet(_fromUtf8(""))
        self.stat_cms.setReadOnly(True)
        self.stat_cms.setObjectName(_fromUtf8("stat_cms"))
        self.gridLayout_9.addWidget(self.stat_cms, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.wdgt3)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_9.addWidget(self.label_6, 0, 0, 1, 1)
        self.gridLayout_10.addWidget(self.wdgt3, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(158, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem, 0, 3, 1, 1)
        self.gridLayout_3.addWidget(self.stats, 0, 0, 1, 1)
        self.plots = QtGui.QWidget(self.page_plots)
        self.plots.setObjectName(_fromUtf8("plots"))
        self.gridLayout_4 = QtGui.QGridLayout(self.plots)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_3.addWidget(self.plots, 1, 0, 1, 1)
        self.gridLayout_3.setRowStretch(1, 50)
        self.stack.addWidget(self.page_plots)
        self.gridLayout.addWidget(self.stack, 0, 0, 1, 1)

        self.retranslateUi(trend_holder)
        self.stack.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(trend_holder)

    def retranslateUi(self, trend_holder):
        trend_holder.setWindowTitle(QtGui.QApplication.translate("trend_holder", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("trend_holder", "Loading..", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("trend_holder", "FWHM:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("trend_holder", "Center:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("trend_holder", "CMS:", None, QtGui.QApplication.UnicodeUTF8))

