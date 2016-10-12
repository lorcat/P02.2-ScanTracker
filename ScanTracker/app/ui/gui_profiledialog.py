__author__ = 'lorcat'

import re
import imp
from PyQt4 import QtGui, QtCore

from app.ui.base_ui.ui_profiledialog import Ui_ProfileDialog
from app.common import logger


class ProfileDialog(QtGui.QDialog, logger.LocalLogger):
    def __init__(self, path=None, parent=None, debug_level=None):
        super(ProfileDialog, self).__init__(parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables(path=path)
        self.__init_ui(path=path)
        self.__init_events()

    def __init_variables(self, path=None):
        """
        Initializes variables used within the class and as output
        :return:
        """
        self.__error = False
        if path is None:
            self.__error = True

        # store profiles as (QFileInfo)
        self._profiles = []

        # gui
        self._ui = None

        # result - loaded module
        self._module = None

    @property
    def module(self):
        return self._module

    @property
    def error(self):
        return self.__error

    def __init_ui(self, path=None):
        """
        Initialization of the gui, fills elements with data
        :return:
        """
        fi = QtCore.QFileInfo(path)

        # make an icon
        image_path = self._provideImagePath(path)
        if image_path is not None:
            pixmap = QtGui.QPixmap(image_path.absoluteFilePath())
            self.setWindowIcon(QtGui.QIcon(pixmap))

        self._ui = Ui_ProfileDialog()
        self._ui.setupUi(self)

        dir = QtCore.QDir(path)

            # get iterator on files
        dirit = QtCore.QDirIterator(dir, QtCore.QDirIterator.NoIteratorFlags)

            # get string list to process profiles
        sl = QtCore.QStringList()

        # parse directory structure, find passing files profile*.py
        # get information from these files
        while dirit.hasNext():
            next = dirit.next()
            finfo = QtCore.QFileInfo(next)
            if finfo.isFile() and re.match(".*profile[^\\\/]*.py$", str(finfo.filePath()).lower()):
                mod = self._loadModule(finfo)
                if mod:
                    try:
                        sl.append(mod.STARTUP["NAME"])
                    except KeyError:
                        sl.append(finfo.baseName())
                    self._profiles.append(finfo)

        if type(sl) is QtCore.QStringList:
            if len(sl):
                self._ui.lbPath.setText(dir.absolutePath())
                self._ui.lbPath.setToolTip("Path: %s" % dir.absolutePath())
                self._ui.lwFiles.insertItems(0, sl)
                self._ui.lwFiles.setCurrentRow(0)

    def __init_events(self):
        """
        Initialization of events working inside gui
        :return:
        """
        self.connect(self._ui.lwFiles, QtCore.SIGNAL("currentRowChanged(int)"), self.processProfileSelection)
        self.connect(self, QtCore.SIGNAL("finished(int)"), self.processExit)

    def processProfileSelection(self, index):
        """
        Processes selection of loaded module name
        :param index: int('index of self._profiles')
        :return:
        """
        return

    def _loadModule(self, finfo):
        """
        Loads specific modules
        :param finfo: QFileInfo()
        :return: module('loaded')
        """
        res = None
        name = str(finfo.baseName())
        fp = pathname = desc = None
        try:
            fp, pathname, desc =  imp.find_module(name, [str(finfo.absolutePath())])
        except ImportError:
            print "Error: cannot load profile '%s', please check path '%s'" % (name, finfo.absolutePath())

        if fp:
            try:
                res = imp.load_module(name, fp, pathname, desc)
            finally:
                if fp:
                    fp.close()
        return res

    def processExit(self, code):
        """
        Function to load specific module on exit
        :param code: int('index of profile to load')
        :return:
        """
        berror = False
        if code:
            index = int(self._ui.lwFiles.currentIndex().row())
            if index >-1:
                mod = self._loadModule(self._profiles[index])
                self._module = mod
            else:
                berror = True
        else:
            berror = True

        if berror:
            QtGui.QApplication.instance().quit()

        self.deleteLater()

    def _provideImagePath(self, path):
        """
        Provides a reference to QFileInfo containing image file path for icon
        :param path: str()
        :return: None or QFileInfo()
        """
        res = None
        dir = QtCore.QDir(path)
        dir.cdUp()
        dir.cd('images')
        temp = QtCore.QFileInfo()
        temp.setFile(dir, 'program_icon.png')
        if temp.isFile():
            res = temp
        else:
            self.error("%s. No image file is present at the path (%s)" % (self.__class__.__name__, path))
        return res


def main():
    app = QtGui.QApplication([])

    diag = ProfileDialog()
    diag.exec_()

    print "You have selected '%s' profile" % str(diag.module)

    app.exec_()

if __name__ == "__main__":
    main()