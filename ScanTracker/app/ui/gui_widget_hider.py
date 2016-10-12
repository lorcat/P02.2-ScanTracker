__author__ = 'Konstantin Glazyrin'

from PyQt4 import QtGui, QtCore

from app.ui.gui_widget_quickmotor import WidgetQuickMotor

from app.ui.base_ui.ui_hideable import Ui_hider
from app.common import logger, common

class WidgetHider(QtGui.QWidget, Ui_hider, logger.LocalLogger, common.Checker):
    def __init__(self, parent=None, debug_level=None):
        super(WidgetHider, self).__init__(parent=parent)

        Ui_hider.setupUi(self, self)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)
        common.Checker.__init__(self)

        self.__init_variables()

    def __init_variables(self):
        self.__widget = None

    def setLabel(self, text):
        self.hideable_label.setText(str(text))

    def setHideableWidget(self, widget):
        self.__widget = None
        layout = self.hideable.layout()

        if self.__widget is not None:
            try:
                self.__widget.deleteLater()
                self.__widget = None
            except AttributeError:
                pass

        self.__widget = widget
        layout.addWidget(self.__widget)

    def getHideableWidget(self):
        return self.__widget

    def setHider(self, label=None, widget=None):
        if label is not None:
            self.setLabel(label)

        if widget is not None:
            self.setHideableWidget(widget)


KEY_NAME = "NAME"

class WidgetHideableMotor(WidgetHider):
    """
    Wrapper making a motor widget hideable
    """
    MOTOR_FORMAT = None
    def __init__(self, parent=None, debug_level=None):
        WidgetHider.__init__(self, parent=parent, debug_level=debug_level)

        self.__init_variables()
        self.__init_ui()

    def __init_variables(self):
        # widgets with motors
        self.__motor_widgets = []

        # external link which should get information on position change
        self.__extlink = []

    def __init_ui(self):
        self.setLabel("Motors")
        self.cleanupWidget()

    def registerLink(self, func):
        if self.check(func):
            for wdgt in self.__motor_widgets:
                wdgt.registerPositionChange(func)
            self.__extlink.append(func)

    def setDoor(self, door=None):
        self.__quickmotor.setDoor(door)

    def addMotors(self, door, *args):
        names = args

        # removing not existing widgets
        i = 0
        temp_wdgts = []
        for (i, wdgt) in enumerate(self.__motor_widgets):
            widget = self.__motor_widgets[i]

            if widget.name not in names:
                self.info("Deleting %s" % widget.motor_name.text())
                widget.cleanupMotor()
                widget.cleanupDoor()
                widget.hide()
                widget.close()
                widget.deleteLater()
                widget = None
            else:
                temp_wdgts.append(widget)

        self.__motor_widgets = None
        self.__motor_widgets = temp_wdgts

        # get valid existing names
        ex_names = [widget.name for widget in self.__motor_widgets]

        # create new widgets in place of existing
        for name in names:
            name = str(name)
            if name is not None and isinstance(name, str) and name not in ex_names:
                motor = WidgetQuickMotor(parent=self, debug_level=self.debug_level)

                # register external entity which should process events
                for link in self.__extlink:
                    if self.check(link):
                        motor.registerPositionChange(link)

                # register a new motor format
                if self.check(self.MOTOR_FORMAT):
                    motor.setMotorFormat(self.MOTOR_FORMAT)

                # set specific door
                motor.setDoor(door)

                # setup motor widget
                motor.setupMotor(name)

                if motor.isMotorInitializied():
                    self.__motor_widgets.append(motor)

        # set the first widget as selected
        if len(self.__motor_widgets) > 0:
            self.setHideableWidget(self.__motor_widgets[0])

        self.cleanupWidget()

    def cleanupWidget(self):
        bflag = False
        if len(self.__motor_widgets)>0:
            bflag = True

        self.hide_button.setChecked(bflag)
        self.hide_button.setEnabled(bflag)

    def setMotorWidget(self, name=None):
        for wdgt in self.__motor_widgets:
            if name == wdgt.name and wdgt != self.getHideableWidget():
                self.setHideableWidget(wdgt)

    def getPointInfo(self, point=None):
        if point is not None and isinstance(point, QtCore.QPointF):
            x = float(point.x())

            wdgt = self.getHideableWidget()
            if wdgt is not None:
                wdgt.addSelectedPosition(x)

    def forcePosition(self):
        wdgt = self.getHideableWidget()
        if wdgt is not None:
            wdgt.forcePosition()

    def setMotorFormat(self, strformat):
        """
        Sets default format for motor
        :param strformat: str() - like '%6.4f'
        :return:
        """
        if self.check(strformat, str) or self.check(strformat, unicode):
            self.MOTOR_FORMAT = strformat

        for wdgt in self.__motor_widgets:
            wdgt.setMotorFormat(strformat)

    def cleanup(self):
        while len(self.__motor_widgets) > 0:
            w = self.__motor_widgets.pop(0)
            w.cleanupMotor()
            w.cleanupDoor()
            w.deleteLater()

        del self.__motor_widgets[:]

    def __del__(self):
        while len(self.__motor_widgets) > 0:
            w = self.__motor_widgets.pop(0)
            w.cleanupMotor()
            w.cleanupDoor()
            w.deleteLater()
