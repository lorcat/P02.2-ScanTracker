__author__ = 'glazyrin'

from PyQt4 import QtGui, QtCore

TEMPLATE = "Loading motor: %s"

class SplashWindow(QtGui.QSplashScreen):
    signfinished = QtCore.pyqtSignal()
    def __init__(self, path):

        # pixmap for the splash screen
        fi = self._prepareImagePath(path)
        pixmap = QtGui.QPixmap(fi.absoluteFilePath())
        QtGui.QSplashScreen.__init__(self, pixmap=pixmap)

        self._proc = QtGui.QProgressBar()
        self._proc.setRange(0, 100)
        self._proc.setTextVisible(True)
        self._proc.setAlignment(QtCore.Qt.AlignHCenter)

        self._label = QtGui.QLabel("")

        layout = QtGui.QGridLayout(self)

        layout.addWidget(self._label, 1, 0)
        layout.addWidget(self._proc, 2, 0, 1, 2)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)
        layout.setRowStretch(0, 50)
        layout.setColumnStretch(0, 50)
        layout.setAlignment(QtCore.Qt.AlignHCenter)

        self._step = 0

        self.repaint()

        self.thread = QtCore.QThread()
        self.thread.start()

        self.moveToThread(self.thread)

        self.show()


    @QtCore.pyqtSlot(str, int, int)
    def setProgress(self, name, value, max):
        """
        Updates progress on motor initialization
        :param name: str('Name of Motor')
        :param value: int('motor index')
        :param max: int('maximum number of motors')
        :return:
        """
        app = QtGui.QApplication.instance()
        app.processEvents()

        bfinished = False
        if value<=max:
            temp = int(float(value)/float(max)*100)
            self._proc.setValue(temp)
            self._label.setText(TEMPLATE % name)

        if value==max:
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()

            self.finish(self)
            self.signfinished.emit()

            self.hide()

            return

        self.raise_()
        self.repaint()

        app = QtGui.QApplication.instance()
        app.processEvents()

    def registerFinished(self, func):
        """
        Connects external function to the internal event fired at the end of operation
        :param func: function to process
        :return:
        """
        self.signfinished.connect(func)

    def _prepareImagePath(self, path):
        """
        Prepares an image path based on path
        :param path: str() - path
        :return: None or QFileInfo()
        """
        res = None
        dir = QtCore.QDir(path)
        dir.cdUp()
        dir.cd('images')
        temp = QtCore.QFileInfo()
        temp.setFile(dir, 'splash.png')
        if temp.isFile():
            res = temp

        return res

    def timeout(self):
        """
        Repainting on a timeout - to keep the window updated
        :return:
        """
        self.repaint()