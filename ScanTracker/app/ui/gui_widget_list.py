__author__ = 'Konstantin Glazyrin'

from PyQt4 import QtGui, QtCore, Qt

from app.common import logger

class ListScansWidget(QtGui.QListWidget, logger.LocalLogger):
    def __init__(self,  name="", parent=None, debug_level=None):
        QtGui.QListWidget.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init__variables()
        self.__init_events()
        self.__init_ui()

    def __init__variables(self):
        pass

    def __init_ui(self):
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        pass

    def __init_events(self):
        pass


class ListChannelWidget(QtGui.QListWidget, logger.LocalLogger):
    def __init__(self,  name="", parent=None, debug_level=None):
        QtGui.QWidget.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)