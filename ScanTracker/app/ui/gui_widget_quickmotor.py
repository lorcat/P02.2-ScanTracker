__author__ = 'Konstantin Glazyrin'

import re

from PyQt4 import QtGui, QtCore

from PyTango import DevState, DeviceAttribute

import taurus
from taurus.core import TaurusAttribute, TaurusException
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.container.tauruswidget import TaurusWidget
from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QDoor, QMacroServer

from app.ui.base_ui.ui_quickmotor import Ui_quickmotor
from app.common import logger, common

from app.pytango.manager import CustomAttributeManager, CustomAttribute
from app.pytango import signals as motor_signals



KEY_MOTORSOURCE = "source"
KEY_MOTORSTATE, KEY_MOTORPOSITION = "state", "position"

KEY_MOTORSTATECHANGE, KEY_MOTORPOSITIONCHANGE, KEY_DOORSTATECHANGE = "MotorState", "MotorPosition", "DoorState"

KEY_POSITIONZERO, KEY_POSITIONINITIAL, KEY_POSITIONSELECTED = 0, 1, 2

class WidgetQuickMotor(QtGui.QWidget, Ui_quickmotor, logger.LocalLogger, common.Checker):
    # maximum number of selected points to keep in the buffer
    MAX_SELECTED = 5
    DISTANCE_FORMAT = '%0.04f'
    MOTOR_FORMAT = '%6.4f'

    # defualt polling parameters
    DEFAULTDOORPOLLING = 1000
    DEFAULTMOTORPOSPOLLING = 500
    DEFAULTMOTORSTATEPOLLING = 1000

    signsetposition = QtCore.pyqtSignal(float)
    signreportposition = QtCore.pyqtSignal(str, float)

    def __init__(self, parent=None, debug_level=None):
        QtGui.QWidget.__init__(self, parent=parent)
        Ui_quickmotor.setupUi(self, self)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)
        common.Checker.__init__(self)

        self.__init_variables()
        self.__init_ui()
        self.__init_events()

    def __init_variables(self):
        self.__motor = None
        self.__motorpos = None
        self.__motorstate = None

        # macro server
        self.macro_server = None

        self.__motor_name = ""
        self.__motor_device_path = ""
        self.__door = None
        self.__door_state = None

        # states saved for processing
        self.__last_door_state = DevState.ON
        self.__last_motor_state = DevState.ON
        self.__last_motor_position = None

        # buffer for storing positions
        self.__positions = [0.000, 0.000]

        self.__manager = CustomAttributeManager().getDefaultManager()

        # value kept for checking if motor is moving or not
        self.__oldposition = None

        self._lambdams = lambda o="", d=KEY_MOTORSTATECHANGE: self.processAttributeChangeEvent(o, d)
        self._lambdamp = lambda o="", d=KEY_MOTORPOSITIONCHANGE: self.processAttributeChangeEvent(o, d)
        self._lambdads = lambda o="", d=KEY_DOORSTATECHANGE: self.processAttributeChangeEvent(o, d)

    def __init_ui(self):
        self.setupMotor()
        self.motor_label.hide()
        self.btn_center.setEnabled(False)

        self._rebuildPositionsSelector()

    def __init_events(self):
        self.signsetposition.connect(self.processPositionChange)

    @property
    def motor(self):
        return self.__motor

    @property
    def door(self):
        return self.__door

    @property
    def attrposition(self):
        return self.__motorpos

    @property
    def name(self):
        return self.__motor_name

    def setDoor(self, door=None):
        """
        Function setting up the Sardana Door
        :param door:
        :return:
        """
        if door is not None:
            if isinstance(door, str):
                wdgt, door = self, taurus.Device(door)
                door = QDoor(door.getFullName())
            if isinstance(door, QDoor):
                self._setup_door(door)

    def cleanupDoor(self):
        """
        An internal function deleting information on the Sardana Door
        :return:
        """


        if self.__door is not None:
            self.info("Cleaning door %s" % self.__door.getFullName())
            self.__door = None

        # cleaning up door state polling
        if self.check(self.__door_state):
            self.__door_state.stopPolling()
            self.disconnect(self.__door_state, QtCore.SIGNAL(motor_signals.SIGNAL_STATE_CHANGE), self._lambdads)
            self.__door_state = None

    def _setup_door(self, door=None):
        """
        An internal function setting up a doo object
        :param door: Qdoor()
        :return:
        """
        if door is not None and isinstance(door, QDoor):
            self.cleanupDoor()
            self.__door = door

            try:
                self.__door_state = self.__manager.getAttribute(device_path=self.__door.getFullName(), attr="state")
                self.__door_state.startPolling()

                self.connect(self.__door_state, QtCore.SIGNAL(motor_signals.SIGNAL_STATE_CHANGE), self._lambdads)
            except TaurusException:
                pass

    def processAttributeChangeEvent(self, *args):
        """
        Performs an analysis of the values reported by Taurus
        :param args:
        :return:
        """
        value, key = args

        if key == KEY_MOTORPOSITIONCHANGE:
            if self.__last_motor_position == None:
                self.addInitialPosition(value)

            self.__last_motor_position = value
            self.reportPosition(value)

        elif key == KEY_MOTORSTATECHANGE:
            self.__last_motor_state = value
        elif key == KEY_DOORSTATECHANGE:
            self.__last_door_state = value

        self.enableMotorControls()


    def setupMotor(self, name=None):
        """
        Function setting up new motor
        :param name: str() - motor name as given through in the pool of a macro server
        :return:
        """
        self.cleanupMotor()

        if self.__door is None or name is None or not isinstance(name, str):
            return

        # get macro server, motor
        self.macro_server = QMacroServer(self.__door.macro_server.getFullName())
        self.__motor = self.macro_server.getElementInfo(name)

        if self.check(self.__motor):
            try:
                motor_source = str(self.__motor.read_attribute("TangoDevice").value)
            except KeyError:
                return

            parent_model = motor_source.lower().replace("/%s" % KEY_MOTORPOSITION, "")
            self._setMotorModel(name=name, model=parent_model)

    def cleanupMotor(self):
        """
        Function resets internal parameters
        :return:
        """

        if self.check(self.__motor):
            self.info("Cleaning motor %s" % self.motor_name.text())

        if self.__motorpos is not None and isinstance(self.__motorpos, CustomAttribute):
            self.__motorpos.stopPolling()

            self.disconnect(self.__motorpos, QtCore.SIGNAL(motor_signals.SIGNAL_STATE_CHANGE), self._lambdams)
            self.disconnect(self.__motorpos, QtCore.SIGNAL(motor_signals.SIGNAL_VALUE_CHANGE), self._lambdamp)

            self.__motor_name = None

        self.__motor = None

        self._setMotorModel()

    def _setMotor(self, model):
        """
        Function establishing motor event listening and motor models
        :param model: str() - motor device Tango reference
        :param position: str() - motor device attribute reference
        :return:
        """
        # redesign - listen to the real motor, not the Sardana Motor
        device_path = self.__motor.read_attribute('TangoDevice').value

        # start polling
        self.__motorpos = self.__manager.getAttribute(device_path=device_path, attr="position", polltime=500)
        self.__motorpos.startPolling()

        self.__motorstate = self.__manager.getAttribute(device_path=device_path, attr="state", polltime=500)
        self.__motorstate.startPolling()

        # subscribe for events
        self.connect(self.__motorpos, QtCore.SIGNAL(motor_signals.SIGNAL_STATE_CHANGE), self._lambdams)
        self.connect(self.__motorpos, QtCore.SIGNAL(motor_signals.SIGNAL_VALUE_CHANGE), self._lambdamp)


    def setMotorFormat(self, strformat):
        """
        Set Motor format for device
        :param strformat: str() - like '%6.4'
        :return:
        """
        berror = True
        if self.check(strformat, str) or self.check(strformat, unicode):
            # test for correct format
            try:
                value = strformat % 10
                berror = False
            except ValueError:
                pass

        if not berror:
            self.MOTOR_FORMAT = strformat

            if self.check(self.__motorpos):
                try:
                    self.__motorpos.getConfig().setFormat(self.MOTOR_FORMAT)
                except AttributeError:
                    pass

        if berror:
            self.error('Wrong format for Motor representation (%s)' % str(strformat))

    def _setMotorModel(self, name="", model=""):
        """
        Function setting motor widget models and motor model
        :param name: name of the motor
        :param model: str() - Tango reference
        :return:
        """
        motor_state, motor_position = "%s/%s" % (model, KEY_MOTORSTATE), "%s/%s" % (model, KEY_MOTORPOSITION)

        self.motor_state.setModel(motor_state)
        self.motor_edit.setModel(motor_position)
        self.motor_label.setModel(motor_position)

        self.motor_name.setText(name)

        if len(model) > 0:
            # if we have change motor name - clear selection
            if self.__motor_name != name:
                pass

            self.__motor_name = name

            self._setMotor(model)
            self.stacked_motor.setCurrentWidget(self.page_motor)
        else:
            self.stacked_motor.setCurrentWidget(self.page_nomotor)

    def forcePosition(self):
        """
        Moves motor to a selected position
        :return:
        """
        if self.__motorpos is not None:
            position = self.__positions[self.cmb_position.currentIndex()]
            self.info("Moving to position "+self.DISTANCE_FORMAT % position)

            # report value
            if self.check(self.__motorpos):
                self.__motorpos.setValue(position)

            self._resetCalculated()

    def addInitialPosition(self, value=None):
        """
        Function adding position as an initial
        :param value: float() - value to added
        :return:
        """
        if value is not None and isinstance(value, float):
            self.__positions[KEY_POSITIONINITIAL] = value

            self._rebuildPositionsSelector()

    def addSelectedPosition(self, value=None):
        """
        Function adds a new position marked as a selected
        :param value: float() - value to added
        :return:
        """
        if value is not None and isinstance(value, float):
            length = len(self.__positions)

            # check size of buffer - wee need +2 (Zero + Initial)
            if len(self.__positions) > self.MAX_SELECTED+1:
                self.__positions.pop(KEY_POSITIONSELECTED)

            distance = float(value - self.__positions[-1])
            self.pos_distance.setText(self.DISTANCE_FORMAT % distance)

            center = float(value + self.__positions[-1])/2.
            self.pos_center.setText(self.DISTANCE_FORMAT % center)

            self.__positions.append(value)

            self._rebuildPositionsSelector()
            self.btn_center.setEnabled(True)

    def _rebuildPositionsSelector(self):
        """
        Rebuilding combo box containing selected positions
        :return:
        """
        strlist = QtCore.QStringList()
        for (i, pos) in enumerate(self.__positions):
            format = ""+self.DISTANCE_FORMAT

            if i == KEY_POSITIONINITIAL:
                format = self.DISTANCE_FORMAT + " - Start"
            elif i == KEY_POSITIONZERO:
                format = self.DISTANCE_FORMAT + " - Zero "
            string = format % pos

            strlist.append(string)

        self.cmb_position.clear()
        self.cmb_position.addItems(strlist)
        self.cmb_position.setCurrentIndex(self.cmb_position.count()-1)

    def processPositionChange(self, value=None):
        """
        Sets a selected value to a position
        :param value:
        :return:
        """
        if value is not None:
            if isinstance(value, str):
                value = float(value)

            self.motor_edit.setValue(value)
            self.__oldposition = value

    def reportPosition(self, value=None):
        """
        Sets a selected value to a position
        :param value:
        :return:
        """
        if self.check(value, float):
            self.emit(QtCore.SIGNAL(motor_signals.SIGNAL_VALUE_CHANGE), value)
            self.signsetposition.emit(value)
            dir(self.__motor.name)
            self.signreportposition.emit(self.__motor.name, value)

    def registerPositionChange(self, func):
        """
        Register an external fucntion which should be executed upon a change of a motor
        :param func:
        :return:
        """
        self.signreportposition.connect(func)

    def enableMotorControls(self):
        """
        Disables or enables motor control
        :param bflag:
        :return:
        """

        benabled = False

        if self.__last_door_state == DevState.ON or self.__last_door_state == DevState.ALARM:
            if self.__last_motor_state == DevState.ON or self.__last_door_state == DevState.ALARM:
                benabled = True

        for wdgt in (self.motor_edit, self.btn_position, self.btn_center, self.cmb_position):
            try:
                wdgt.setEnabled(benabled)
            except RuntimeError as e:
                self.error(str(wdgt))

    def isMotorInitializied(self):
        """
        Returns information on motor initialization state
        :return:
        """
        res = False
        if self.__motor is not None:
            res = True
        return res

    def forceCenter(self):
        """
        Move to the center position relative to the last selected point
        :return:
        """
        if self.__motorpos is not None:
            try:
                position = float(self.pos_center.text())
            except ValueError:
                return

            self.info("Moving to position "+self.DISTANCE_FORMAT % position)

            self.__motorpos.setValue(position)

            self._resetCalculated()

    def _resetCalculated(self):
        """
        Resets a calculated value for center position (between two last selected points)
        :return:
        """
        for w in (self.pos_distance, self.pos_center):
            w.setText("")

        self.btn_center.setEnabled(False)

    def closeEvent(self, event):
        self.info("quick motor closing ----------------------------------")