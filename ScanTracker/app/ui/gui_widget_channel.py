__author__ = 'Konstantin Glazyrin'

from PyQt4 import QtGui, QtCore, Qt

from app.ui.base_ui.ui_list_channel_widget import Ui_list_channel_widget
from app.common import logger

class ChannelWidget(QtGui.QWidget, Ui_list_channel_widget, logger.LocalLogger):

    signsetx = QtCore.pyqtSignal(bool, QtGui.QWidget)
    signsety = QtCore.pyqtSignal(bool, QtGui.QWidget)
    signsetnorm = QtCore.pyqtSignal(bool, QtGui.QWidget)

    signchange = QtCore.pyqtSignal()

    def __init__(self, name="", parent=None, debug_level=None):
        QtGui.QWidget.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        Ui_list_channel_widget.setupUi(self, self)

        self.__init_variables()
        self.__init_ui()
        self.__init_events()

    @property
    def label(self):
        return str(self.lb_channel.text())

    @label.setter
    def label(self, value):
        self.setLabel(value)

    def __init_variables(self):
        pass

    def __init_ui(self):
        pass

    def __init_events(self):
        pass

    def setLabel(self, value):
        string = ""
        try:
            string = str(value)
        except ValueError:
            pass
        self.lb_channel.setText(string)

    def isX(self):
        return  self.ch_x.isChecked()

    def isY(self):
        return  self.ch_y.isChecked()

    def isNorm(self):
        return self.ch_norm.isChecked()

    def actionSetX(self, bflag, breport=True):
        if self.ch_x.isChecked()!=bflag:
            self.ch_x.setChecked(bflag)
            return
        self.reportX(bflag, breport=breport)

    def actionSetY(self, bflag, breport=True):
        if self.ch_y.isChecked()!=bflag:
            self.ch_y.setChecked(bflag)
            return
        self.reportY(bflag, breport=breport)

    def actionSetNorm(self, bflag, breport=True):
        if self.ch_norm.isChecked()!=bflag:
            self.ch_norm.setChecked(bflag)
            return
        self.reportNorm(bflag, breport=breport)

    def reportChange(self, breport=True):
        if breport:
            self.signchange.emit()

    def reportX(self, bflag, breport=True):
        if breport:
            self.signsetx.emit(bflag, self)
        self.reportChange(breport=breport)

    def reportY(self, bflag, breport=True):
        if breport:
            self.signsety.emit(bflag, self)
        self.reportChange(breport=breport)

    def reportNorm(self, bflag, breport=True):
        if breport:
            self.signsetnorm.emit(bflag, self)
        self.reportChange(breport=breport)

    def registerChange(self, func):
        self.signchange.connect(func)

    def registerXChange(self, func):
        self.signsetx.connect(func)

    def registerYChange(self, func):
        self.signsety.connect(func)

    def registerNormChange(self, func):
        self.signsetnorm.connect(func)

    def unregisterChange(self, func):
        self.signchange.disconnect(func)

    def unregisterXChange(self, func):
        self.signsetx.disconnect(func)

    def unregisterYChange(self, func):
        self.signsety.disconnect(func)

    def unregisterNormChange(self, func):
        self.signsetnorm.disconnect(func)

    def setState(self, bx=None, by=None, bnorm=None):
        if bx is not None:
            self.ch_x.setChecked(bx)
        if by is not None:
            self.ch_y.setChecked(by)
        if bnorm is not None:
            self.ch_x.setChecked(bnorm)


class ChannelWidgetDelegate(QtGui.QStyledItemDelegate, logger.LocalLogger):
    def __init__(self, parent=None, debug_level=None):
        QtGui.QStyledItemDelegate.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init__variables()

    def __init__variables(self):
        self.__widget = ChannelWidget(parent=self.parent(), debug_level=self.debug_level)

    def createEditor(self, parent, option, index):
        self.info_object(self.widget())
        if parent is not None:
            self.__widget.setParent(parent)
        return self.__widget

    def widget(self):
        return self.__widget