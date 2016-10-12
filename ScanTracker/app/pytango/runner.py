__author__ = 'glazyrin'

from PyQt4 import QtCore
from PyTango import DevFailed, DeviceProxy

class CustomAttributeRunner(QtCore.QRunnable):
    def __init__(self, device_path, attr, value):
        QtCore.QRunnable.__init__(self)

        self.device_path = device_path
        self.attr = attr
        self.value = value

        self.setAutoDelete(True)

    def run(self):
        try:
            d = DeviceProxy(self.device_path)
            d.write_attribute_asynch(self.attr, self.value)
        except DevFailed:
            pass

class CustomCommandRunner(QtCore.QRunnable):
    def __init__(self, device_path, command, value):
        QtCore.QRunnable.__init__()

        self.device_path = device_path
        self.command = command
        self.value = value

        self.setAutoDelete(True)

    def run(self):
        try:
            d = DeviceProxy(self.device_path)
            d.command_inout_asynch(self.command, self.value)
        except DevFailed:
            pass