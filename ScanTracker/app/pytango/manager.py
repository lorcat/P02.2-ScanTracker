__author__ = 'glazyrin'

from PyTango import DeviceProxy, DevFailed

from PyQt4 import QtCore, Qt
from app.pytango import signals
from app.pytango.runner import *

KEYMANAGER_FULLPATH, KEYMANAGER_DEVICEPATH, KEYMANAGER_DEVICEATTR, KEYMANAGER_ATTRTIMER, KEYMANAGER_ATTRCOUNTER, KEYMANAGER_ATTROBJ  = "FULLPATH", "DEVICEPATH", "DEVICEATTR", "ATTRTIMER", "ATTRCOUNTER", "ATTROBJECT"

ATTRMANAGER = None

class CustomAttributeManager(QtCore.QObject):
    DEFAULT_THREAD_NUMBER = 1
    DEFAULT_THREAD_PRIORITY = QtCore.QThread.NormalPriority
    DEFAULT_THREADPOOL_NUMBER = 5

    def __init__(self, thread_count=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)

        if thread_count is None:
            thread_count = self.DEFAULT_THREAD_NUMBER

        # keep only one instance active
        self.__init_variables()

        if self.getDefaultManager() == self:
            self.__init_threads(thread_count)

    def __init_variables(self):
        # htreads container
        self.__threads = []

        # current thread reference
        self.__thindex = None

        # thread pool for attribute writing
        self.__thpool = QtCore.QThreadPool(parent=self)
        self.__thpool.setMaxThreadCount(self.DEFAULT_THREADPOOL_NUMBER)

        # attribute container
        self.__attributes = []

    def __init_threads(self, thread_count):
        for i in range(thread_count):
            th = CustomThread()
            self.__threads.append(th)
            th.start()

            th.setPriority(self.DEFAULT_THREAD_PRIORITY)

    def cleanup(self):
        """
        Cleanups threads
        :return:
        """

        for attr in self.__attributes:
            try:
                timer = attr[KEYMANAGER_ATTRTIMER]
                obj = attr[KEYMANAGER_ATTROBJ]

                QtCore.QMetaObject.invokeMethod(timer, "moveBack", Qt.Qt.QueuedConnection)
                QtCore.QMetaObject.invokeMethod(obj, "moveBack", Qt.Qt.QueuedConnection)

                self.disconnect(timer, QtCore.SIGNAL("timeout()"), obj.run)
                self.disconnect(obj, QtCore.SIGNAL(signals.SIGNAL_POLLING_CHANGED), self.processPollingChange)
                self.disconnect(obj, QtCore.SIGNAL(signals.SIGNAL_VALUE_SET), self.processValueSet)
                self.disconnect(obj, QtCore.SIGNAL(signals.SIGNAL_COMMAND_RUN), self.processCommandRun)
            except (KeyError, Exception) as e:
                pass

        # DESTROYING THE THREADS
        for (i, thread) in enumerate(self.__threads):
            # thread.terminate()
            QtCore.QMetaObject.invokeMethod(thread, "quit", Qt.Qt.QueuedConnection)


    def _prepAttribute(self, device_path, attr, polltime):
        """
        Prepares an entry for internal storage of attributes
        :param device_path: str()
        :param attr: str()
        :return:
        """
        full_attr = self._buildAttribute(device_path, attr)

        # prepare an object and its timer
        attrobj = CustomAttribute(device_path, attr, main_thread=QtCore.QThread.currentThread())
        attrtimer = CustomTimer(main_thread=QtCore.QThread.currentThread())
        attrtimer.setInterval(polltime)
        attrtimer.setSingleShot(False)

        # initialize events
        self.connect(attrtimer, QtCore.SIGNAL("timeout()"), attrobj.run)

        res = {KEYMANAGER_FULLPATH: full_attr.lower(), KEYMANAGER_DEVICEPATH: device_path, KEYMANAGER_DEVICEATTR: attr,
               KEYMANAGER_ATTRTIMER: attrtimer, KEYMANAGER_ATTRCOUNTER: 1, KEYMANAGER_ATTROBJ: attrobj}

        # connect a signal
        self.connect(attrobj, QtCore.SIGNAL(signals.SIGNAL_POLLING_CHANGED), self.processPollingChange)
        self.connect(attrobj, QtCore.SIGNAL(signals.SIGNAL_VALUE_SET), self.processValueSet)
        self.connect(attrobj, QtCore.SIGNAL(signals.SIGNAL_COMMAND_RUN), self.processCommandRun)

        return res

    def processPollingChange(self, full_attr, bflag):
        """
        Starts or stops polling of the attribute
        :param full_attr: str()
        :param bflag: bool()
        :return:
        """
        for (i, el) in enumerate(self.__attributes):
            full_path = el[KEYMANAGER_FULLPATH]
            if full_path == full_attr.lower() or (full_attr == el[KEYMANAGER_DEVICEPATH]):
                timer = el[KEYMANAGER_ATTRTIMER]
                if bflag and not timer.isActive():
                    QtCore.QMetaObject.invokeMethod(timer, "start", Qt.Qt.QueuedConnection)
                elif not bflag and timer.isActive():
                    QtCore.QMetaObject.invokeMethod(timer, "stop", Qt.Qt.QueuedConnection)
                break

    def processValueSet(self, device_path, attr,  value):
        """
        Starts or stops polling of the attribute
        :param full_attr: str()
        :param bflag: bool()
        :return:
        """
        runner = CustomAttributeRunner(device_path, attr, value)
        self.__thpool.tryStart(runner)

    def processCommandRun(self, device_path, command, value):
        """
        Starts or stops polling of the attribute
        :param full_attr: str()
        :param bflag: bool()
        :return:
        """
        runner = CustomCommandRunner(device_path, command, value)
        self.__thpool.tryStart(runner)


    def getDefaultManager(self):
        """
        Gets a default attr manager
        :return:
        """
        global ATTRMANAGER
        if ATTRMANAGER is None:
            ATTRMANAGER = self

        return ATTRMANAGER

    def getAttribute(self, device_path, attr, polltime=3000):
        """
        Returns an existing or a new object responsible for attributes
        :param device_path:
        :param attr:
        :return:
        """
        full_attr = self._buildAttribute(device_path, attr)

        res = None

        for (i, el) in enumerate(self.__attributes):
            if el[KEYMANAGER_FULLPATH].lower() == full_attr.lower():
                res = el
                break

        # create new attribute, timer, put them into the storage
        if res is None:
            res = self._prepAttribute(device_path, attr, polltime)

        if res is not None:
            self.__attributes.append(res)

            th = self.getNextThread()
            res[KEYMANAGER_ATTROBJ].moveToThread(th)
            res[KEYMANAGER_ATTRTIMER].moveToThread(th)

        res = res[KEYMANAGER_ATTROBJ]
        return res

    def _buildAttribute(self, device_path, attr):
        """
        Builds full tango device path
        :param device_path: str()
        :param attr: str()
        :return: str()
        """
        res = "%s/%s" % (device_path, attr)
        return res

    def getNextThread(self):
        """
        Returns a next thread for processing
        :return: QtCore.QThread
        """
        res = None
        if len(self.__threads) > 0:
            if self.__thindex == None or self.__thindex == len(self.__threads) - 1:
                self.__thindex = 0
            else:
                self.__thindex += 1

            try:
                res = self.__threads[self.__thindex]
            except IndexError:
                pass
        return res


class CustomAttribute(QtCore.QObject):
    def __init__(self, device_path=None, attr=None, parent=None, main_thread=None):
        QtCore.QObject.__init__(self, parent=parent)

        self.__dev_path = device_path

        self.__attr = None
        self.__full_attr = None

        self.__attr = attr
        self.__full_attr = self._buildAttribute(device_path, attr)

        # to keep track of value changes
        self.__state = None
        self.__value = None
        self.__error = False

        # polling state
        self.__polling = False

        # main thread
        self.__main_thread = main_thread

    def run(self):
        """
        Default function responsible for device communication with external world - signals reporting
        :return:
        """
        # print "Tick Tack %s" % self.__full_attr
        try:
            d = DeviceProxy(self.__dev_path)
            state = d.state()

            # device is operating - notify that there is no error anymore
            if self.__error:
                self.lastError(False)

            # test for state change
            if state != self.__state and self.__attr != "state":
                self.lastState(state)
            elif state != self.__state and self.__attr == "state":
                self.lastState(state)
                self.lastValue(state)
                return

            # test for attr change
            if self.__attr is not None:
                value = d.read_attribute(self.__attr).value
                if value != self.__value:
                    self.lastValue(value)

        except DevFailed:
            self.__state = None
            self.__value = None
            self.lastError(True)

    @QtCore.pyqtSlot()
    def moveBack(self):
        # print "Terminating object"
        if self.__main_thread is not None:
            self.blockSignals(True)
            self.moveToThread(self.__main_thread)
            self.deleteLater()

    def _buildAttribute(self, device_path, attr):
        """
        Builds full tango device path
        :param device_path: str()
        :param attr: str()
        :return: str()
        """
        res = "%s/%s" % (device_path, attr)
        return res

    def lastError(self, value=None):
        """
        Reports a value on last error through a signal
        :return:
        """
        if value is None:
            value = self.__value
        else:
            self.__error = value
        self.emit(QtCore.SIGNAL(signals.SIGNAL_ERROR_CHANGE), self.__full_attr, self.__error)

    def lastValue(self, value=None):
        """
        Reports a value on last value through a signal
        :return:
        """
        if value is None:
            value = self.__value
        else:
            self.__value = value
        self.emit(QtCore.SIGNAL(signals.SIGNAL_VALUE_CHANGE), value)

    def lastState(self,value=None):
        """
        Reports a value on last state through a signal
        :return:
        """
        if value is None:
            value = self.__state
        else:
            self.__state = value
        self.emit(QtCore.SIGNAL(signals.SIGNAL_STATE_CHANGE), value)

    def startPolling(self):
        """
        Emits a signal starting the polling
        :return:
        """
        self.__polling = True
        self.emit(QtCore.SIGNAL(signals.SIGNAL_POLLING_CHANGED), self.__full_attr, self.__polling)

    def stopPolling(self):
        """
        Emits a signal finishing the polling
        :return:
        """
        self.__polling = False
        self.emit(QtCore.SIGNAL(signals.SIGNAL_POLLING_CHANGED), self.__full_attr, self.__polling)

    def isPolling(self):
        """
        Returns polling state
        :return:
        """
        return self.__polling

    def setValue(self, value):
        """
        Sets an attribute value if possible
        :param value:
        :return:
        """
        self.emit(QtCore.SIGNAL(signals.SIGNAL_VALUE_SET), self.__dev_path, self.__attr, value)

    def runCommand(self, command, value):
        """
        Sets an attribute value if possible
        :param value:
        :return:
        """
        self.emit(QtCore.SIGNAL(signals.SIGNAL_COMMAND_RUN), self.__dev_path, command, value)


class CustomTimer(QtCore.QTimer):
    def __init__(self, main_thread=None):
        QtCore.QTimer.__init__(self)

        self.__main_thread = main_thread

    @QtCore.pyqtSlot()
    def moveBack(self):
        # print "Terminating timer"
        if self.__main_thread is not None:
            self.stop()
            self.moveToThread(self.__main_thread)
            self.deleteLater()

class CustomThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.setTerminationEnabled(True)

    @QtCore.pyqtSlot()
    def quit(self):
        # print "Quiting thread"
        QtCore.QThread.quit(self)
        self.wait()