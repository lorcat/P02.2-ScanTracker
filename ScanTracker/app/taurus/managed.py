__author__ = 'Konstantin Glazyrin'

from PyQt4 import QtCore, QtGui
from PyTango import DeviceAttribute
from taurus.core import TaurusManager, TaurusFactory, TaurusAttribute
from taurus.core.tango.tangoattribute import TangoAttribute, TangoStateAttribute

from app.common import logger, common

TAURUSATTRIBUTEMANAGER = None
SIGNALWRAPPER = None

class SignalWrapper(QtCore.QObject, logger.LocalLogger, common.Checker):

    signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, debug_level=None):
        QtCore.QObject.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables()
        self.getDefaultSignalWrapper(obj=self)

    def __init_variables(self):
        self.__mutex = QtCore.QMutex()

    def getDefaultSignalWrapper(self, obj=None):
        """
        Creates a singleton for manager object
        :param obj:
        :return:
        """
        res = None
        global SIGNALWRAPPER
        if self.check(SIGNALWRAPPER):
            res = SIGNALWRAPPER
        elif obj is not None:
            res = SIGNALWRAPPER = obj
        return res

    def registerSignal(self, func):
        """
        Connects a signal for external reporting
        :param func:
        :return:
        """
        self.signal.connect(func)

    def reportSignal(self, tangoattr, devattr):
        """
        Reports a change of data value with mutex - for threading
        :param value:
        :return:
        """
        #if self.__mutex.tryLock():

        self.signal.emit([tangoattr, devattr])
        # self.__mutex.unlock()

class TaurusAttributeManager(QtCore.QObject, logger.LocalLogger, common.Checker):
    # signals to control
    signstartpoll = QtCore.pyqtSignal(str)
    signstoppoll = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, debug_level=None):
        QtCore.QObject.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables()
        self.__init_events()

    def __init_variables(self):
        # container for polled objects
        self.__attrs = {}

        self.__attrs_polling = {}

        self.__thread = None

        if self == self.getDefaultManager(obj=self):
            # event thread
            self.__thread = self._createThread()


    def __init_events(self):
        """
        Initialize events
        :return:
        """
        sw = SignalWrapper().getDefaultSignalWrapper()
        sw.registerSignal(self.processAttrChange)

    def getDefaultManager(self, obj=None):
        """
        Creates a singleton for manager object
        :param obj:
        :return:
        """
        res = None
        global TAURUSATTRIBUTEMANAGER
        if self.check(TAURUSATTRIBUTEMANAGER):
            res = TAURUSATTRIBUTEMANAGER
        elif obj is not None:
            res = TAURUSATTRIBUTEMANAGER = obj
        return res

    def _createThread(self):
        thread = QtCore.QThread(parent=self)
        thread.start()
        return thread

    def isRunning(self):
        res = None
        if self.check(self.__thread, QtCore.QThread):
            res = self.__thread.isRunning()
        return res

    def _stopThread(self):
        if self.check(self.__thread) and self.__thread.isRunning():
            self.__thread.terminate()
            self.__thread.wait()

    def requestAttribute(self, device_path=None, polling_interval=None):
        """
        Retrieves a new TaurusAttribute or makes a new one
        :param device_path: str()
        :return:
        """
        res = None
        if self.checkString(device_path):
            if device_path in self.__attrs.keys():
                res = self.__attrs[device_path]
            else:
                attr = TaurusAttributeWrapper(device_path=device_path, polling_interval=polling_interval, parent=self)
                self.signstartpoll.connect(attr.startPolling)
                self.signstoppoll.connect(attr.stopPolling)

                self.__attrs[device_path] = attr

                attr.moveToThread(self.__thread)
                res = attr
        return res

    def processAttrChange(self, *args):
        """
        Get and distribute information on attribute change
        :param args:
        :return:
        """
        tangoattr, devattr = args[0]
        self.emit(QtCore.SIGNAL(tangoattr.getFullName()), tangoattr, devattr)

    def startPolling(self, obj=None):
        """
        Starts an object polling
        :param obj:
        :return:
        """
        device_path = None
        if self.checkString(obj):
            device_path = obj
        elif self.check(obj, TaurusAttributeWrapper):
            device_path = obj.device_path

        if self.check(device_path):
            self.signstartpoll.emit(device_path)

            if device_path not in self.__attrs_polling.keys():
                self.__attrs_polling[device_path] = 0
            else:
                self.__attrs_polling[device_path] += 1

    def stopPolling(self, obj=None):
        """
        Stops an object polling - if no subscribed objects left
        :param obj:
        :return:
        """
        device_path = None
        if self.checkString(obj):
            device_path = obj
        elif self.check(obj, TaurusAttributeWrapper):
            device_path = obj.device_path

        if self.check(device_path) and device_path in self.__attrs_polling.keys():
            self.__attrs_polling[device_path] -= 1

            if self.__attrs_polling[device_path] <= 0:
                self.__attrs_polling[device_path] = 0

            if self.__attrs_polling[device_path] == 0:
                self.signstoppoll.emit(device_path)

    def __del__(self):
        """
        Stops all polling attributes and stops the thread
        :return:
        """
        if self.check(self.__thread):
            for (i, attr) in enumerate(self.__attrs_polling):
                while self.__attrs_polling[attr] > 0:
                    self.stopPolling(attr)

            for device_path in self.__attrs:
                self.__attrs[device_path].deleteLater()

            self._stopThread()

class TaurusAttributeWrapper(QtCore.QObject, logger.LocalLogger, common.Checker):

    DEFAULTPOLLINGINTERVAL = 1000

    def __init__(self, device_path=None, polling_interval=None, parent=None, debug_level=None):
        QtCore.QObject.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.device_path = str(device_path)
        self.attr = None

        self.polling_interval = polling_interval

        self.__init_variables()

    def __init_variables(self):
        # attribute itself
        self.attr = self._createTaurusAttribute()

        # flag indicating polling
        self.__polling = False

        if not self.check(self.polling_interval):
            self.polling_interval = self.DEFAULTPOLLINGINTERVAL

        # value change check
        self.__old_value = None

        # callback function
        self.func_callback = None


    def _createTaurusAttribute(self):
        manager = TaurusManager()
        return manager.getAttribute(self.device_path)

    def isPolling(self):
        """
        Reports current polling state
        :return:
        """
        return self.__polling

    def startPolling(self, device_path=None):
        """
        Starts attribute polling
        :return:
        """
        # check if polling is requested for this object
        if self.check(device_path) and str(device_path) not in self.device_path:
            return

        if self.isPolling():
            return

        if self.check(self.attr, TaurusAttribute):
            # self.info('Starting Polling %s' % self.device_path)
            self.attr.addListener(self.listener)
            self.attr.activatePolling(self.polling_interval)
            self.__polling = True

    def stopPolling(self, device_path=None):
        """
        Stops attribute polling
        :return:
        """
        device_path = str(device_path)
        if self.check(device_path):
            if device_path in self.device_path and self.__polling:
                if self.check(self.func_callback):
                    self.attr.deleteListener(self.func_callback)
                self.attr.disablePolling()
                self.func_callback = None
        self.__polling = False

    def listener(self, *args):
        """
        Listen to an update of the attribute - only a change is reported
        :param args:
        :return:
        """
        # three default values
        tangoattr, evtype,  devattr = args

        if self.check(tangoattr, TaurusAttribute) and self.check(devattr, DeviceAttribute):
            if devattr.value != self.__old_value:
                # self.debug("Value has changed %s %s %s" % (tangoattr.getFullName(), devattr.value, self.__old_value))
                sw = SignalWrapper().getDefaultSignalWrapper()
                sw.reportSignal(tangoattr, devattr)
                self.__old_value = devattr.value

            if devattr.has_failed:
                self.error('Attribute (%s) has failed' % self.tangoattr.getFullName())

    def __del__(self):
        self.stopPolling()

    def getCurrentValue(self):
        return self.__old_value