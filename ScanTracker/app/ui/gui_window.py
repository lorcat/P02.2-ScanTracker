__author__ = 'Konstantin Glazyrin'

import os

from base_ui.ui_window import Ui_MainWindow
from PyQt4 import QtGui, QtCore
import numpy as np

from app.common import logger, storage

from app.storage.main import ScanStorage, Scan, Channel
from app.storage.events import *

# storage based
from app.storage.main import ScanStorage, Scan
from app.taurus.custom import *

import taurus
from taurus.qt.qtgui.application import TaurusApplication
# from taurus.external.qt import Qt
from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QDoor, QMacroServer
# from sardana.taurus.core.tango.sardana.sardana import BaseSardanaElement
# from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QMacroServer

from app.config.keys import *
from app.ui.gui_profiledialog import ProfileDialog
from app.ui.gui_widget_trend_holder import WidgetTrendHolder
from app.ui.gui_widget_hider import WidgetHideableMotor
from app.ui.gui_window_scan import CustomScanWindow
from app.ui.gui_splash import SplashWindow

from app.pytango.manager import CustomAttributeManager

KEY_STATUS = 'STATUS'

class MainWindow(QtGui.QMainWindow, Ui_MainWindow, logger.LocalLogger):
    """
    Signals emited on scan start, scan end and scan acquisition
    """
    # signal carrying no data
    signscanstart = QtCore.pyqtSignal()
    signscanend = QtCore.pyqtSignal()
    signscanacq = QtCore.pyqtSignal()

    # signal carrying data
    signscanpacket = QtCore.pyqtSignal(tuple, bool, bool, QDoor)

    # signal for the point
    signscanpoint = QtCore.pyqtSignal(QtCore.QPointF)

    # signal to force position
    signforceposition = QtCore.pyqtSignal()


    signsplash = QtCore.pyqtSignal(str, int, int)

    def __init__(self, config_path=None, parent=None, debug_level=None):
        super(MainWindow, self).__init__(parent=None)
        super(MainWindow, self).setupUi(self)
        logger.LocalLogger.__init__(self, debug_level=debug_level)

        self.__config = None
        # processing configuration profiles
        if not self._checkConfigPath(config_path=config_path):
            self.error('Wrong config path is provided (%s)' % config_path)
            return

        # load profiles, check module content
        p = ProfileDialog(path=config_path, parent=self, debug_level=self.debug_level)
        result = p.exec_()

        if result == 0:
            self.info('Bye Bye! Hope to see you again soon!')
            return
        elif p.module is None:
            self.error('Bye Bye! No profile was selected - I cannot work like this.')
            return

        self.__splash = SplashWindow(config_path)
        self.__splash.registerFinished(self.show)
        self.registerSplashMessage(self.__splash.setProgress)

        # main configuration variable
        self.__config = p.module.STARTUP

        # separate object creation and actual initialization for correct Splash screen repaint
        self._initializeStartUp(config_path)

    def _initializeStartUp(self, config_path):
        self.__startup_timer = QtCore.QTimer()
        self.__startup_timer.setSingleShot(True)
        self.__startup_timer.setInterval(100)
        self.__startup_timer.start()

        self.connect(self.__startup_timer, QtCore.SIGNAL('timeout()'), lambda: self._main_init(config_path))
        self.__startup_timer.start()


    def _main_init(self, config_path):

        self.__splash.show()

        # app = QtGui.QApplication.instance()
        # app.processEvents()

        self.reportSplashMessage('Loading configuration', 0, 100)

        # app.processEvents()

        self._setWindowIcon(config_path)

        self.reportSplashMessage('Initializing variables', 25, 100)
        # app.processEvents()
        self.__init_variables()

        self.reportSplashMessage('Initializing interface', 50, 100)
        # app.processEvents()
        self.__init_ui()

        self.reportSplashMessage('Initializing events', 75, 100)
        # app.processEvents()
        self.__init_events()

        self.reportSplashMessage('Initializing events', 100, 100)

        self.__splash.deleteLater()
        self.__splash = None

        self.__startup_timer.stop()
        self.__startup_timer.deleteLater()
        self.__startup_timer = None


    def __init_variables(self, config_path=None):
        # storage for scans
        self.__scans = ScanStorage(parent=self)

        # storage for widgets with scan plots
        self.__scan_widgets = storage.StorageRecaller(parent=self, debug_level=self.debug_level)

        # number of columns for data representation
        self.__cols = 2

        # door name and Door object initialized on __init_events
        temp_key = ''
        try:
            # door related
            temp_key = KEYPROFILE_DOORS
            self.__door_names = self.__config[temp_key]
            self.__doors = []
            # keeps track of functions called on signals
            self.__door_funcs = {}

            # motor hider widget
            self.__motor_hider = WidgetHideableMotor(parent=self, debug_level=self.debug_level)

            # main widget for scan traversal
            self.__pymcawidget = CustomScanWindow(storage=self.__scans, debug_level=self.debug_level)

            # widget to hold scans in form of TrendScan
            self.__dpm = WidgetTrendHolder(parent=self, debug_level=self.debug_level)

            temp_key = KEYPROFILE_COLNUMBER
            self.__dpm.setNumberColumns(self.__config[temp_key])

            temp_key = KEYPROFILE_CURVE
            self.__dpm.setCurveConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_POINTMARKER
            self.__dpm.setPointMarkerConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_POSITIONMARKER
            self.__dpm.setPositionMarkerConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_MOTORMARKER
            self.__dpm.setMotorMarkerConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_TIMESCAN
            self.__dpm.setTimescanMotors(self.__config[temp_key])

            temp_key = KEYPROFILE_TIMESCANPOINTS
            self.__dpm.setTimescanPointNumber(self.__config[temp_key])

            temp_key = KEYPROFILE_TTAXISFONT
            self.__dpm.setAxisFontConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_TTAXISLABELFONT
            self.__dpm.setAxisLabelFontConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_TTBACKGROUND
            self.__dpm.setBackgroundConfig(self.__config[temp_key])

            temp_key = KEYPROFILE_TTGRID
            self.__dpm.setGridConfig(self.__config[temp_key])

        except AttributeError:
            self.__config = None
            self._defaultConfigKeyError(temp_key)
            return

        # attributes which have reasonable default values, no need to change
        try:
            temp_key = KEYPROFILE_MOTORFORMAT
            self.__motor_hider.setMotorFormat(self.__config[temp_key])
        except AttributeError as e:
            self.__config = None
            self._defaultConfigKeyError(temp_key)
            return

        # counter controlling view of the plots - single plot or all of them
        self.__page_counter = 0

        # initialize a link between motor widget and the taurustrendholder
        self.__motor_hider.registerLink(self.__dpm.processExternalPosition)

    def __init_ui(self):
        if self.__config is None:
            return

        # fixing gui - set the page with quick scans as default
        self.graphs.setCurrentIndex(0)

        # create dynamic plot manager - custom
        self.__dpm.allocate(4)
        layout = self.scan_page.layout()
        layout.addWidget(self.__dpm)

        self._prepDpmTest()

        # add hideable motor to the layout
        self.motor_view.layout().addWidget(self.__motor_hider)

        # list view for scans
        self.view_page.layout().addWidget(self.__pymcawidget)

        # create menu, prepare door selection
        self._prepareMenuDoorActions()

    def __init_events(self):
        if self.__config is None:
            return

        # connect with qdoor
        self.__connectWithQDoor()

        # produce global events - carrying data
        self.registerScanPacket(self.processScanData)

        # get scan changed info
        self.connect(self.__scans, QtCore.SIGNAL(EVENT_SCAN_CHANGED), self.action_scan_added)

        # register motor actions
        self.registerPointInfo(self.__motor_hider.getPointInfo)
        self.registerForcePosition(self.__motor_hider.forcePosition)

        # register a function reporting a pick event
        for tt in self.__dpm.trends:
            tt.registerPick(lambda data="", wdgt=tt: self.action_picked(data, wdgt))

        # door menu events
        self.connect(self.menuDoors, QtCore.SIGNAL('triggered (QAction*)'), self.processMenuDoorAction)

    def _prepareMenuDoorActions(self):
        """
        Prepares Door actions, sets states - only first state is set as active by default
        :return:
        """
        menu = self.menuDoors

        for (i, door_name) in enumerate(self.__door_names):
            action = QtGui.QAction(door_name, menu)
            action.setCheckable(True)

            bchecked = False
            if i == 0:
                bchecked = True
            action.setChecked(bchecked)
            menu.addAction(action)

    def _defaultConfigKeyError(self, key):
        self.error('Config key (%s) is undefined' % key)

    def _checkConfigPath(self, config_path=None):
        res = True
        if not os.path.isdir(config_path):
            res = False
            self.error('Config path for program profiles is not a directory (%s)' % config_path)
        return res

    def _setWindowIcon(self, config_path):
        """
        Provides a reference to QFileInfo containing image file path for icon
        :param path: str()
        :return: None or QFileInfo()
        """
        res = None
        dir = QtCore.QDir(config_path)
        dir.cdUp()
        dir.cd('images')
        temp = QtCore.QFileInfo()
        temp.setFile(dir, 'program_icon.png')
        if temp.isFile():
            self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(temp.absoluteFilePath())))

    @property
    def config(self):
        return self.__config

    def __connectWithQDoor(self, breleaseall=False):
        """
        Connects/Disconnects window with the Door object
        :param qdoor: (QDoor or str) either a QDoor instance or the QDoor name
        """
        try:
            for (i, action) in enumerate(self.menuDoors.actions()):
                door_name = str(action.text())
                if breleaseall:
                    action.setChecked(False)

                try:
                    if self.__doors[i] is not None:
                        door = self.__doors[i]
                except IndexError:
                    door = QDoor(taurus.Device(door_name).getFullName())
                    if door.getState() is None:
                        QtGui.QMessageBox.critical(None, "Error", "MacroServer for door (%s) is offline" % door_name)
                        action.setChecked(False)

                    self.__doors.append(door)

                if action.isChecked():
                    self._checkEnviroment(door)
                    # connect signal
                    func_callback = lambda packet="", d=door: self.scanDataReceived(packet, d)
                    self.__door_funcs[door] = func_callback
                    self.connect(door, QtCore.SIGNAL('recordDataUpdated'), func_callback)
                else:
                    # disconnect signal
                    if door in self.__door_funcs.keys():
                        self.disconnect(door, QtCore.SIGNAL('recordDataUpdated'), self.__door_funcs[door])
        except AttributeError:
            pass

    def _checkEnviroment(self, door):
        """
        checks door environment - sets it queitly for the door
        :param door:
        :return:
        """
        entry = 'JsonRecorder'
        if entry not in door.getEnvironment() or not door.getEnvironment(entry):
            door.putEnvironment('JsonRecorder', True)
            self.info('Enabling JsonRecorder for Door (%s)' % door.name())
        else:
            self.info('JsonRecorder was already enabled for door (%s)' % door.name())

    ###
    ## operation with stack view
    ###
    def action_left_stack(self):
        """
        Change graph stack page one to the left
        :return:
        """
        self.action_change_stack(step=-1)

    def action_right_stack(self):
        """
        Change graph stack page one to the right
        :return:
        """
        self.action_change_stack(step=1)

    def action_home_stack(self):
        """
        Change graph stack to home - all channels
        :return:
        """
        self.__page_counter = 0
        self.action_change_stack(0)

    def action_change_stack(self, step=1):
        """
        Changes view of graph stack some page index with a step
        :param step:
        :return:
        """
        stack = self.graphs
        index = self.__page_counter

        bvalid = True
        index = index + step
        if index < 0 and abs(index)-1 < len(self.__dpm.trends):
            self.__dpm.setVisibleWidget(abs(index)-1)
        elif index == 0:
            stack.setCurrentIndex(index)
            self.__dpm.makeAllVisible()
        elif index == 1:
            stack.setCurrentIndex(index)
        else:
            bvalid = False

        if bvalid:
            self.__page_counter = index

    ###
    ## work with QToolBox - scans
    ###
    def action_scan_added(self):
        """
        Populates lists of channel names in the
        :return:
        """
        pass

    def action_ch_listview(self, cindex):
        """
        Populates view of special channels based on chname
        :param chname: str() - chname of interest
        :return:
        """
        pass

    def closeEvent(self, ev):
        """
        Function executed on upon program end
        :param ev: QEvent() object
        :return:
        """
        self.__connectWithQDoor(breleaseall=True)

        # cleaning up the storage
        self.__scans.cleanup()

        ev.accept()

    def scanDataReceived(self, raw_packet, door):
        """
        Function processing scan data
        :param packet: JSON dict() object - scan data or something else
        :return:
        """
        if raw_packet is None:
            return

        pkgid, packet = raw_packet
        if packet is None:
            pass

        pcktype = packet.get("type", "__UNKNOWN_PCK_TYPE__")

        start, end = False, False

        bvalid = True
        if pcktype == "data_desc":
            self.debug("Data description - scan start")
            self.signscanstart.emit()
            start = True
        elif pcktype == "record_data":
            self.debug("Getting data")
            self.signscanacq.emit()
        elif pcktype == "record_end":
            self.debug("Scan finished")
            self.signscanend.emit()
            end = True
        else:
            self.debug("Ignoring packet of type %s" % repr(pcktype))
            bvalid = False

        if bvalid:
            self.signscanpacket.emit(raw_packet, start, end, door)

    def action_picked(self, *args):
        """
        Function recieves information about the picked position and amplitude
        :param args: list()+TaurusTrendWidget
        :return:
        """
        data, wdgt = args

        point, curvname, pindex, cmd = data[KEY_POINT], data[KEY_CURVNAME], data[KEY_INDEX], data[KEY_CMD]

        # do nothing in case of data absence
        if point is None:
            return

        self.info("%s Point was picked at (%0.4f:%0.4f)" % (KEY_STATUS, float(point.x()), float(point.y())))

        if not self.__dpm.isTimescanMode():
            self.reportNewPointInfo(point)


            self.lbl_position.setText('%6.4f' % point.x())

    def action_position(self):
        """
        Function which stimulates force position for the motor
        :return:
        """
        value = str(self.lbl_position.text())

        bvalid = False
        if len(value) > 0:
            try:
                value = float(value)
                bvalid = True
            except ValueError:
                bvalid = False

        if bvalid:
            self.reportForcePosition()

    def info(self, msg):
        """
        Addition to the logger function - show selected messages in the status bar
        :param msg: str()
        :return:
        """
        msg = str(msg)

        if KEY_STATUS in msg:
            msg = msg.replace(KEY_STATUS, "")

            statusbar = self.statusbar
            if self.parent() is not None:
                try:
                    statusbar = self.statusbar
                except AttributeError:
                    statusbar = None
            if statusbar is not None:
                self.statusbar.showMessage(str(msg), 5000)

        self._logger.info(msg)

    def registerScanStart(self, func):
        """
        Simple function to notify of scan start - no data is transmitted
        :param func: function()
        :return:
        """
        self.signscanstart.connect(func)

    def registerScanEnd(self, func):
        """
        Simple function to notify of scan end - no data is transmitted
        :param func: function()
        :return:
        """
        self.signscanend.connect(func)

    def registerScanData(self, func):
        """
        Simple function to notify of scan data line - no data is transmitted
        :param func: function()
        :return:
        """
        self.signscanacq.connect(func)


    def registerScanPacket(self, func):
        """
        Simple function to notify of scan start with packet header
        :param func: function()
        :return:
        """
        self.signscanpacket.connect(func)

    def processScanData(self, packet, start=False, end=False, door=None):
        """
        Main Action fired on new scan header - what we do is passing information to the TrendSet objects directly
        :param packet: dict() - from JSON recorder
        :return:
        """
        if start:
            # processing header data
            self._createNewScan(packet, door)
            pass
        elif end:
            # scan end - footer
            self._finishScan(packet)
            pass
        elif not end and not start:
            # process data - append to scans and scan channels
            self._addScanData(packet)
            pass

    def _createNewScan(self, packet, door=None):
        """
        Create new scan in our scan storage, create new channels
        :param packet: tuple()
        :return:
        """
        # check previous scan and finish it - just by a flag
        scan = self.__scans.getCurrentScan()
        if scan is not None and scan.is_active():
            scan.finish(True)

        # create a new scan from packet
        scan = Scan(parent=self.__scans)
        scan.newScanFromPacket(packet)

        # motor names
        motor_names = scan.getMotorLabels()

        # test if we have changed the measurement group or perform a first scan
        if self.__scans.isMeasurementChanged() or len(self.__scans.storage) == 0:
            self.info("Measurement Group has changed")
            self.__page_counter = 0
            self.action_change_stack(step=0)
        else:
            self.info("Measurement Group has not changed")

        self.__scans.addScan(scan)
        self.__dpm.setScan(scan)

        btsmode = self.__dpm.isTimescanMode()
        if btsmode:
            motor_names = [scan.getMotorLabels()[-1]]
        else:
            # remove timescan mode from the choice of motors
            motor_names.pop(-1)

        self.selectCurrentMotor(motor_names)

        if not btsmode:
            self.__motor_hider.cleanup()
            self.__motor_hider.addMotors(door, *motor_names)

        scan.start(True)

    def _addScanData(self, packet):
        """
        Appends data to the current scan channels
        :param packet: tuple()
        :return:
        """
        # parse information from packet, fill the current scan
        scan = self.__scans.getCurrentScan()
        if scan is not None:
            scan.dataFromPacket(packet)

        # test that scanning info is working
        # scan_info = "Scan %i: %s" % (scan.serial, scan.cmd)
        # self.__pymca.addCurve(scan.channels[0].points, scan.channels[1].points, legend=scan_info, replace=True)
        pass

    def _finishScan(self, packet):
        scan = self.__scans.getCurrentScan()
        if scan is not None:
            scan.finish(True)

    def selectCurrentMotor(self, names):
        # we keep motors selected if motor exists, otherwise - cleanup

        current_text = str(self.motor_selection.currentText())

        # which index to set as a default one
        new_index = 0
        if current_text in names:
            new_index = names.index(current_text)

        # creating new list of motors
        strlist = QtCore.QStringList()

        for name in names:
            strlist.append(name)

        self.motor_selection.clear()
        self.motor_selection.addItems(strlist)
        self.motor_selection.setCurrentIndex(new_index)

        # reporting to the hider - that we get new motor name as default
        self.__motor_hider.setMotorWidget(name=strlist[new_index])

        # test for go button enabling - disabling
        bflag = True
        scan = self.__scans.getCurrentScan()
        if len(strlist) == 1 and scan.getMotorLabels()[-1] in strlist:
            bflag = False
        elif len(strlist)==0:
            bflag = False

        self.go_position.setEnabled(bflag)

    def registerPointInfo(self, func):
        self.signscanpoint.connect(func)

    def reportNewPointInfo(self, point):
        self.signscanpoint.emit(point)

    def registerForcePosition(self, func):
        self.signforceposition.connect(func)

    def reportForcePosition(self):
        self.signforceposition.emit()

    def registerSplashMessage(self, func):
        self.signsplash.connect(func)

    def reportSplashMessage(self, *args):
        self.signsplash.emit(*args)

    def _prepDpmTest(self):
        """
        Demonsteration function
        :return:
        """
        def Lorentz(x):
            return 0.31831/((x-1)**2+1)

        tt = self.__dpm.trends[0]

        x = np.arange(-4.0, 5.0, .01)
        y = np.array([Lorentz(v) for v in x])

        tt.attachRawData({'x': x, 'y': y, 'title': ''})
        tt.autoScaleAllAxes()

        tt.calculatePlotStatistics()

        tt = self.__dpm.trends[1]

        x = np.arange(-4.0, 5.0, .25)
        y = np.array([Lorentz(v) for v in x])

        tt.attachRawData({'x': x, 'y': y, 'title': ''})
        tt.autoScaleAllAxes()

        tt.calculatePlotStatistics()

        tt = self.__dpm.trends[2]

        x = np.arange(-4.0, 5.0, .25)
        y = np.array([Lorentz(v) for v in x])

        tt.attachRawData({'x': x, 'y': y, 'title': ''})
        tt.autoScaleAllAxes()

        tt.calculatePlotStatistics()

        tt = self.__dpm.trends[3]

        x = np.arange(-4.0, 5.0, .5)
        y = np.array([Lorentz(v) for v in x])

        tt.attachRawData({'x': x, 'y': y, 'title': ''})
        tt.autoScaleAllAxes()

        tt.calculatePlotStatistics()

    def processMenuDoorAction(self, action):
        """
        Toggles door selection, turns on/off door signal subscription
        :param action:
        :return:
        """
        self.__connectWithQDoor()

    def action_update_environment(self):
        """
        Function which updates environment with position
        :return:
        """
        self.update_env.blockSignals(True)

        pos = self.lbl_position.text()

        try:
            pos = float(pos)
        except ValueError:
            pos = None

        if pos is not None:
            key = "ScanTracker"
            user_input = QtGui.QMessageBox.question(self, "Updating Sardana Environment", "Are your sure that you want to update Sardana Door environment variable (%s -> %6.4f)?" % (key, pos),
                                                    buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Cancel)
            if user_input == QtGui.QMessageBox.Ok:
                try:
                    for (i, action) in enumerate(self.menuDoors.actions()):
                        door_name = str(action.text())

                        if action.isChecked():
                            door = self.__doors[i]
                            door.putEnvironment(key, pos)
                            self.debug("Setting environment (%s) value (%s) key (%s)" % (door_name, pos, key))
                except AttributeError:
                    pass

        self.update_env.blockSignals(False)