__author__ = 'Konstantin Glazyrin'

__all__ = ["ScanStorage", "Scan", "Channel"]

from PyQt4 import QtCore

from app.common.logger import LocalLogger
from app.storage.events import *


class ScanStorage(QtCore.QObject, LocalLogger):
    def __init__(self, parent=None, debug_level=None, max_scans=50):
        super(ScanStorage, self).__init__(parent=parent)
        LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables(max_scans=max_scans)

    def __init_variables(self, max_scans=50):
        self.__main_storage = []
        self.__max_scans = max_scans

        self.info("Maximal number of scans (%i)" % self.__max_scans)

    @property
    def storage(self):
        return self.__main_storage

    def __iter__(self):
        return iter(self.__main_storage)

    def __getitem__(self, item):
        res = None
        if isinstance(item, int) and item < len(self.__main_storage):
            res = self.storage[item]
        return res

    def __len__(self):
        return len(self.__main_storage)

    def cleanup(self):
        """
        Cleaning up the storage
        :return:
        """

        while len(self.__main_storage) > 0:
            scan = self.__main_storage.pop(0)
            if scan is not None and isinstance(scan, Scan):
                scan.cleanup()
                scan.deleteLater()

        del self.__main_storage[:]

    def addScan(self, scan=None):
        """
        Appends a scan to the end of internal storage
        :param scan: Scan() object
        :return:
        """
        index = len(self.storage)
        self.insertScan(index, scan)

    def insertScan(self, index=None, scan=None):
        """
        Appends a scan to the storage
        :param index: int() - index of position to insert the scan into
        :param scan: Scan() object
        :return:
        """
        if scan is not None and isinstance(scan, Scan) and isinstance(index, int):
            self.info("Adding new scan; Current storage size (%i); Maximum storage length (%i)" % (len(self), self.__max_scans))
            if len(self) > self.__max_scans:
                self.deleteScan(0)
            self.storage.insert(index, scan)

            # register event for scans
            scan.registerChangeEvent(self.actionScanChanged)
            scan.registerStartEvent(self.actionScanStarted)
            scan.registerFinishEvent(self.actionScanFinished)

            # report that a scan is added - used for page filling
            self.actionScanStarted(scan)

    def deleteScan(self, index=None):
        """
        Delete a scan using an index
        :param index: int() - index of scan to delete
        :return:
        """
        if isinstance(index, int) and index <len(self.__main_storage):
            self.info("Deleting Scan (%i)" % index)

            scan = self.storage.pop(index)
            if scan is not None and isinstance(scan, Scan):
                self.connect(scan, QtCore.SIGNAL('destroyed()'), self.confirmScanDestruction)
                scan.cleanup()
                scan.deleteLater()
        return

    def confirmScanDestruction(self, *args):
        """
        Confirm deletion of the scan
        :param args:
        :return:
        """
        self.debug("A scan was destroyed.")

    def getScan(self, index=None):
        """
        Retrieve a Scan() object by index
        :param index:
        :return:
        """
        res = None
        if index>=0 and len(self.storage):
            res = self.storage[index]
        return res

    def getCurrentScan(self):
        """
        Retrieves the last added Scan() object
        :return: Scan() or None
        """
        return self.getPreviousScan()

    def getPreviousScan(self, step=-1):
        """
        Retrieves previous scan - the one relative to the end of scan
        :return:
        """
        res = None
        index = len(self.storage)

        if index > 0:
            try:
                res = self.storage[step]
            except IndexError:
                pass
        return res

    def getPreceedingScan(self):
        """
        Returns a scan preceeding the last one
        :return:
        """
        return self.getPreviousScan(step=-2)

    def isMeasurementChanged(self):
        """
        Performs a test determining if we have a change in counter channels names: channel names changed or motor number changed
        @to do  - motor number
        :return:
        """
        res = False
        scan_new, scan_old = self.getCurrentScan(), self.getPreceedingScan()

        # first scan
        source_new, source_old = None, None

        if scan_new is not None:
            source_new = scan_new.getCounterSources()

        if scan_old is not None:
            source_old = scan_old.getCounterSources()

        self.info(source_new)
        self.info(source_old)

        if source_new is not None and source_new != source_old:
            res = True
        elif source_new is not None and source_old is not None:
            # check motor count
            mot_new, mot_old = scan_new.getMotorSources(), scan_old.getMotorSources()

            if len(mot_new) != len(mot_old):
                res = True
        return res

    def getScanBySerial(self, serial=None):
        """
        Retrieves a Scan() object using its serial
        :param serial: int() - serial number of the scan
        :return: Scan() or None
        """
        res = None
        if isinstance(serial, int):
            for (i, scan) in enumerate(self.storage):
                if scan.serial == serial:
                    res = scan
        return res

    def actionScanChanged(self, scan):
        if isinstance(scan, int):
            scan = self.getScanBySerial(scan)

        if isinstance(scan, Scan):
            self.emit(QtCore.SIGNAL(EVENT_SCAN_CHANGED), scan)


    def actionScanStarted(self, scan):
        self.debug("Scan started")
        if isinstance(scan, int):
            scan = self.getScanBySerial(scan)

        if isinstance(scan, Scan):
            self.emit(QtCore.SIGNAL(EVENT_SCAN_STARTED), scan)

        self.actionScanChanged(scan)

    def actionScanFinished(self, scan):
        self.debug("Scan finished")
        if isinstance(scan, int):
            scan = self.getScanBySerial(scan)

        if isinstance(scan, Scan):
            self.emit(QtCore.SIGNAL(EVENT_SCAN_FINISHED), scan)

        self.actionScanChanged(scan)

KEY_SERIALNO, KEY_MACROID, KEY_SCANFILE, KEY_CMD, \
KEY_MOTOR, KEY_SCANDIR, KEY_DATA, KEY_COUNTERS, KEY_COLUMNDESC = "serialno", "macro_id", "scanfile", "title", \
                                                 "ref_moveables", "scandir", "data", "counters", "column_desc"

class Scan(QtCore.QObject, LocalLogger):

    signscanstarted = QtCore.pyqtSignal(int)
    signscanfinished = QtCore.pyqtSignal(int)
    signscanchanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, debug_level=None, serial=None, macroid=None, cmd=None, motors=None, scanfile=None, scandir=None):
        super(Scan, self).__init__(parent=parent)
        LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables()
        self.setHeaderInfo(serial=serial, macroid=macroid, cmd=cmd, motors=motors, scanfile=scanfile, scandir=scandir)

    def __init_variables(self):
        self.__channels = []

        # flags to check if the scan is active
        self.__started = False
        self.__finished = False

        # selector for last changed scan - use serial number as a unique id
        self.__last_changed = None

        # storage for header
        self.__header = {KEY_CMD: None,  KEY_SCANFILE: "", KEY_SCANDIR: "",
                         KEY_SERIALNO: None, KEY_MACROID: "",
                         KEY_MOTOR: []}

        self.start()

    def cleanup(self):
        """
        Cleaning up scan memory
        :return:
        """
        self.debug("Cleaning up channels.")
        while len(self.__channels) > 0:
            ch = self.__channels.pop(0)
            if ch is not None and isinstance(ch, Channel):
                self.connect(ch, QtCore.SIGNAL('destroyed()'), self.confirmChannelDestruction)
                ch.cleanup()
                ch.deleteLater()

        # remove internal variables
        self.__header.clear()
        del self.__header
        del self.__channels[:]

    def confirmChannelDestruction(self, *args):
        """
        Confirm channel destruction
        :param args:
        :return:
        """
        self.debug("A channel has been destroyed..")

    @property
    def channels(self):
        return self.__channels

    @property
    def cmd(self):
        return self.__header[KEY_CMD]

    @cmd.setter
    def cmd(self, value):
        self.__header[KEY_CMD] = value

    @property
    def serial(self):
        return self.__header[KEY_SERIALNO]

    @serial.setter
    def serial(self, value):
        self.__header[KEY_SERIALNO] = value

    @property
    def motors(self):
        return self.__header[KEY_MOTOR]

    @motors.setter
    def motors(self, value):
        if value is None:
            value = []
        self.__header[KEY_MOTOR] = value

    @property
    def macroid(self):
        return self.__header[KEY_MACROID]

    @macroid.setter
    def macroid(self, value):
        self.__header[KEY_MACROID] = value

    @property
    def scanfile(self):
        return self.__header[KEY_SCANFILE]

    @scanfile.setter
    def scanfile(self, value):
        self.__header[KEY_SCANFILE] = value

    @property
    def scandir(self):
        return self.__header[KEY_SCANDIR]

    @scandir.setter
    def scandir(self, value):
        self.__header[KEY_SCANDIR] = value

    @property
    def started(self):
        return self.__started

    @property
    def finished(self):
        return self.__finished

    @property
    def active(self):
        return self.is_active()

    def __getitem__(self, item):
        res = None
        if isinstance(int) and item < len(self.__channels):
            res = self.channels[item]
        return res

    def __len__(self):
        return len(self.channels)

    def __iter__(self):
        return iter(self.channels)

    def __str__(self):
        res = "\n%s([" % (self.__class__.__name__)

        for (i, el) in enumerate(self.channels):
            res += "\n\t%02i : %s" % (i, str(el))
        res +="\n])"
        return res

    def append_channel(self, label=None, source=None, points=None, bmotor=False):
        """
        Appends a channel into the embedded storage
        :param label: str()
        :param points: list() or tuple()
        :param bmotor: bool()
        :return:
        """
        index = len(self.channels)
        self.insert_channel(index, label=label, source=source, points=points, bmotor=bmotor)

    def insert_channel(self, index, label=None, source=None, points=None, bmotor=False):
        """
        Inserts a single channel into the embedded storage
        :param index: int()
        :param label: str()
        :param points: list() or tuple()
        :param bmotor: bool()
        :return:
        """
        channel = Channel(parent=self)
        channel.set(label=label, source=source, points=points, bmotor=bmotor)

        self.insert_pure_channel(index, channel)

    def append_pure_channel(self, channel):
        """
        Appends prepared channel as the last item of the internal storage
        :param channel:
        :return:
        """
        index = len(self.channels)
        self.insert_pure_channel(index, channel)

    def insert_pure_channel(self, index, channel):
        """
        Single function embedding channel into the internal storage
        :param index: int()
        :param channel: Channel()
        :return:
        """
        if isinstance(channel, Channel) and isinstance(index, int):
            self.channels.insert(index, channel)
            self.start(True)

            # report an event for channel content change - only for the first channel
            if index == 0:
                self.reportChannelChange()

    def select_channel(self, index, bselect=True):
        """
        Sets the 'selected' flag of a channel with a given index
        :param index:
        :param bselect:
        :return:
        """
        if isinstance(index, int) and index < len(self.channels):
            self.channels[index].select(bselect=True)

    def is_channel_selected(self, index):
        """
        Reports if channel of given index has a 'selected' flag enabled
        :param index: int()
        :return:
        """
        res = None
        if isinstance(index, int) and index<len(self.channels):
            res = self.channels[index].is_selected()
        return res

    def get_channel(self, index):
        """
        Returns full channel object by index
        :param index: int()
        :return:
        """
        return self[index]

    def get_channel_data(self, index):
        """
        Returns channel data by index
        :param index: int()
        :return:
        """
        res = 0
        channel = self[index]
        if channel is not None:
            res = (channel.x, channel.y)
        return res

    def is_active(self):
        """
        Function reporting state of scan data collection
        :return:
        """
        res = False
        if self.started and not self.finished:
            res = True
        return res

    def start(self, bflag=True):
        """
        Setss the flag indicating that scan has started
        :param bflag: bool()
        :return:
        """
        self.__started = bflag
        if bflag:
            self.signscanstarted.emit(self.serial)

    def finish(self, bflag=True):
        """
        Sets the flag indicating that scan was collected, emits corresponding signal
        :param bflag: bool()
        :return:
        """
        self.__finished = bflag
        if bflag:
            self.signscanfinished.emit(self.serial)
            self.reportChannelChange()

    def reportChannelChange(self):
        """
        Emit a signal indicating change of channel content
        :return:
        """
        self.info("Reporting channel change")
        self.signscanchanged.emit(self.serial)

    def setHeaderInfo(self, serial=None, macroid=None, cmd=None, motors=None, scanfile=None, scandir=None):
        """
        Sets header info of the current Scan() object
        :param serial: int()
        :param cmd: str()
        :param motors: str()
        :return:
        """
        self.serial, self.macroid, self.cmd, self.motors, self.scanfile, self.scandir = serial, macroid, cmd, motors, scanfile, scandir

    def registerStartEvent(self, func):
        """
        Register an external callback for the local event: scan start
        :param func:
        :return:
        """
        self.signscanstarted.connect(func)

    def registerFinishEvent(self, func):
        """
        Register an external callback for the local event: scan finish
        :param func:
        :return:
        """
        self.signscanfinished.connect(func)

    def registerChangeEvent(self, func):
        """
        Unregister an external callback for the local event: scan data change
        :param func:
        :return:
        """
        self.signscanchanged.connect(func)

    def uregisterStartEvent(self, func):
        """
        Unregister an external callback for the local event: scan start
        :param func:
        :return:
        """
        self.signscanstarted.disconnect(func)

    def unregisterFinishEvent(self, func):
        """
        Unregister an external callback for the local event: scan finish
        :param func:
        :return:
        """
        self.signscanfinished.disconnect(func)

    def unregisterChangeEvent(self, func):
        """
        Register an external callback for the local event: scan data change
        :param func:
        :return:
        """
        self.signscanchanged.disconnect(func)

    def getChannelByLabel(self, label=""):
        """
        Returns a channel object for a given
        :param label: str() - label for the y axis of the channel
        :return: Channel() or None
        """
        res = None

        if (isinstance(label, str) or isinstance(label, unicode)) and len(label):
            for ch in self.channels:
                if ch.label.lower() == label.lower():
                    res = ch
                    break
        return res

    def isChannelPresent(self, label=""):
        """
        Reports if channel with a given ylabel is present in the scan
        :param label: str() - label for the y axis of the channel
        :return: (bool(), Channel() or None)
        """
        res = False
        ch = self.getChannelByLabel(ylabel=label)
        if isinstance(ch, Channel):
            res = True
        return (res, ch)

    def appendData(self, label="", points=None,):
        """
        Appends data to the channel given by ylabel
        :param label: str() - label for the y axis of the channel
        :param points: float, int, list() or tuple() - data points
        :return:
        """
        test, ch = None, None
        if (isinstance(label, str) or isinstance(label, unicode)) and len(label):
            test, ch = self.isChannelPresent(label=label)

        if test:
            if isinstance(points, float) or isinstance(points, int):
                points = (points)

            if (isinstance(points, list) or isinstance(points, tuple)):
                ch.points += points
                ch.report_data_change()

    def newScanFromPacket(self, packet):
        """
        Fills header information on the scan from json packet
        :param packet: tuple()
        :return:
        """
        if packet is None or not isinstance(packet, tuple):
            return

        # header
        pkgid, header = packet

        # data from header
        data = header[KEY_DATA]
        self.setHeaderInfo(serial=data[KEY_SERIALNO], macroid=header[KEY_MACROID], cmd=data[KEY_CMD],
                             motors=data[KEY_MOTOR], scanfile=data[KEY_SCANFILE], scandir=data[KEY_SCANDIR])

        self.info('Scan command %s' % self.cmd)

        counters = []
        # get information on name - label correspondance
        for el in data[KEY_COLUMNDESC]:
            if isinstance(el, dict) and el.has_key(KEY_CHSOURCE) and el[KEY_CHSOURCE] in data[KEY_COUNTERS] and el[KEY_OUTPUT] and el[KEY_PLOTTYPE] > 0:
                counters.append({el[KEY_CHLABEL] : el[KEY_CHSOURCE]})

        self.info("Counters %s" % counters)

        # create channels - each channel is independent either it is counter or motor position
        # motor positions come first
        data[KEY_MOTOR] = list(data[KEY_MOTOR])
        data[KEY_MOTOR].append('timestamp')

        for ch in data[KEY_MOTOR]:
            self.append_channel(label=ch, source=ch, bmotor=True)

        # counters come last
        for counter in counters:
            key = counter.keys()[0]
            label, source = key, counter[key]
            self.append_channel(label=label, source=source)

    def dataFromPacket(self, packet):
        """
        Fills data information on the scan from json packet
        :param packet: tuple()
        :return:
        """
        if packet is None or not isinstance(packet, tuple):
            return

        # header
        pkgid, header = packet

        # data from header
        data = None
        try:
            data = header[KEY_DATA]
        except KeyError:
            pass

        # append data to the channels - test by Tango device name
        if data is not None and isinstance(data, dict):
            for (i, ch) in enumerate(self.channels):
                if ch.source in data.keys():
                    if i==0:
                        self.reportChannelChange()

                    try:
                        value = float(data[ch.source])
                    except ValueError:
                        value = 0.0

                    ch.points.append(value)

    def getLabels(self, bmotor=True, bcounter=True):
        """
        Returns channel list names in form of strings
        :return: list(str)
        """
        res = None
        for ch in self.channels:
            bfound = False
            if ch.is_motor() and bmotor:
                bfound = True
            elif not ch.is_motor() and bcounter:
                bfound = True

            if bfound:
                if res is None:
                    res = []
                res.append(ch.label)
        return res

    def getMotorLabels(self):
        """
        Return labels for motor channels
        :return:
        """
        return self.getLabels(bcounter=False)

    def getCounterLabels(self):
        """
        Return labels for counter channels
        :return:
        """
        return self.getLabels(bmotor=False)

    def getSources(self, bmotor=True, bcounter=True):
        """
        Returns channel list names in form of strings
        :return: list(str)
        """
        res = None
        for ch in self.channels:
            bfound = False
            if ch.is_motor() and bmotor:
                bfound = True
            elif not ch.is_motor() and bcounter:
                bfound = True

            if bfound:
                if res is None:
                    res = []
                res.append(ch.source)
        return res

    def getMotorSources(self):
        """
        Return labels for motor channels
        :return:
        """
        return self.getSources(bcounter=False)

    def getCounterSources(self):
        """
        Return labels for counter channels
        :return:
        """
        return self.getSources(bmotor=False)


KEY_CHLABEL, KEY_CHMOTOR, KEY_CHSOURCE, KEY_OUTPUT, KEY_PLOTTYPE = "label", "MOTOR", "name", "output", "plot_type"

class Channel(QtCore.QObject, LocalLogger):
    # signal reporting data change to the Scan() object
    signdata = QtCore.pyqtSignal()

    def __init__(self, parent=None, debug_level=None):
        super(Channel, self).__init__(parent=parent)
        LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables()

    def __init_variables(self):
        # storage for header
        self.__header = {KEY_CHLABEL: None, KEY_MOTOR: False, KEY_CHSOURCE: None}

        # storage for 1D data
        self.__points = []

        # selection flag
        self.__selected = False

    def __str__(self):
        res = "%s(header=%s, points=%s)" % (self.__class__.__name__, str(self.__header), str(self.__points))
        return str(res)

    def cleanup(self):
        """
        Cleaning up channel memory
        :return:
        """
        self.debug("Cleaning up a channel %s" % self.__header[KEY_CHLABEL])
        # delete internal variables
        self.__header.clear()

        del self.points[:]
        del self.__header

    @property
    def label(self):
        return self.__header[KEY_CHLABEL]

    @label.setter
    def label(self, value):
        self.__header[KEY_CHLABEL] = value

    @property
    def source(self):
        return self.__header[KEY_CHSOURCE]

    @source.setter
    def source(self, value):
        self.__header[KEY_CHSOURCE] = value

    @property
    def points(self):
        return self.__points

    @points.setter
    def points(self, value):
        self.__set_points(value)

    def set_motor(self, bflag=False):
        """
        Sets a flag determining if channel is a motor
        :param bflag: bool()
        :return:
        """
        self.__header[KEY_CHMOTOR] = bflag

    def is_motor(self):
        """
        Return current information - if channel is a motor
        :return:
        """
        return self.__header[KEY_CHMOTOR]

    def set_label(self, label=None):
        """
        Sets header info of the current Channel() object
        :param label:
        :return:
        """
        self.label = label

    def set_source(self, source=None):
        """
        Sets header info of the current Channel() object
        :param source: str(TangoObect.name)
        :return:
        """
        self.source = source

    def set_data(self, points=()):
        """
        Sets data of the current Channel() object, emits a signal on data indicating a data change
        :param points: list()
        :return:
        """
        self.__set_points(points)
        self.signdata.emit()

    def __set_points(self, points=None):
        """
        Sets individual x() channel of Channel() object
        :param points: list()
        :return:
        """
        if points is None or not isinstance(points, list) or not isinstance(points, tuple):
            points = []
        self.__points = points


    def select(self, bselect=True):
        """
        Set the select flag for the current Channel() object
        :param bselect:
        :return:
        """
        if isinstance(bselect, bool):
            self.__selected = bselect

    def is_selected(self):
        """
        Reports the 'select' flag for the current Channel() object
        :return:
        """
        return self.__selected

    def registerChangeEvent(self, func):
        """
        Registers an event fired on change of internal data
        :param func:
        :return:
        """
        self.signdata.connect(func)

    def report_data_change(self):
        """
        Wrapper to the event of data change
        :return:
        """
        self.signdata.emit()

    def set(self, label=None, source=None, points=None, bmotor=False):
        self.label = label
        self.source = source
        self.points = points
        self.set_motor(bmotor)