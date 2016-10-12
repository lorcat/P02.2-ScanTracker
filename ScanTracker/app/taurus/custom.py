__author__ = 'Konstantin Glazyrin'

__all__ = ["CustomDynPlotManager", "CustomTaurusTrend", "KEY_CMD", "KEY_INDEX", "KEY_CURVNAME", "KEY_POINT",
           "CMD_POSITION", "CMD_POINT"]

import re
import copy
import datetime
import numpy as np

from taurus.qt.qtgui.taurusgui.macrolistener import ChannelFilter
from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QDoor

import taurus
from taurus.external.qt import QtCore, QtGui, Qt, Qwt5

from taurus.qt.qtgui.taurusgui import DynamicPlotManager
from taurus.qt.qtgui.plot import TaurusTrend, TaurusTrendsSet, ScanTrendsSet, TaurusCurveMarker

from app.common import logger
from app.common.common import Checker
from app.config.graphics import DIMGREY, WHITE, BLACK

# configuration on shortcuts
from app.config.shortcuts import *
from app.qwt.custom import VerticalMarker

# Keys to use for command discrimination
CMD_POINT, CMD_POSITION = "Point", "Position"
KEY_POINT, KEY_CURVNAME, KEY_INDEX, KEY_CMD = "Point", "CurvName", "PointIndex", "CMD"

class CustomDynPlotManager(DynamicPlotManager, logger.LocalLogger):
    def __init__(self, parent=None, chfilter=None, debug_level=None):

        self.__panels = {}

        DynamicPlotManager.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, name=self.__class__.__name__, debug_level=debug_level)

        # to have an anytime door access
        self._door = None
        # to have a filter for undesirable channels
        self._chfilter = chfilter or []

    @property
    def chfilter(self):
        return self._chfilter

    @chfilter.setter
    def chfilter(self, value):
        if isinstance(value, str) and len(value):
            self._chfilter.append(value)
        elif isinstance(value, tuple) or isinstance(value, list):
            self._chfilter = self._chfilter + value
        elif value is None:
            self._chfilter = []

    @property
    def door(self):
        res = self._door
        if res is None:
            self._door = self.getModelObj()
        return self._door

    @door.setter
    def door(self, value):
        if isinstance(value, QDoor):
            self._door = value
        else:
            self._door = None
            raise RuntimeError

    @property
    def trends1d(self):
        return self._trends1d

    @property
    def trends2d(self):
        return self._trends2d

    @property
    def panels(self):
        return self.__panels

    def _updateTemporaryTrends1D(self, trends1d):
        """adds necessary trend1D panels and removes no longer needed ones

        :param trends1d: (dict) A dict whose keys are tuples of axes and
                         whose values are list of model names to plot
                         e.g.
                         {
                         ('<mov>',): ['haspp02ch2:10000/expchan/vfcadc_eh2b/4',
                          'haspp02ch2:10000/expchan/vfcadc_eh2b/3',
                          'haspp02ch2:10000/expchan/vfcadc_eh2b/2', 'haspp02ch2:10000/expchan/vfcadc_eh2b/1']}

        :returns: (tuple) two lists new,rm:new contains the names of the new
                  panels and rm contains the names of the removed panels
        """
        self.info("Creation of curves")
        newpanels = []

        # will create a swarm of widgets
        for axes, plotables in trends1d.items():
            if not axes:
                continue

            # it is made only once - model change let's assume model will remain
            self._trends1d = []  # panel names are created in the right order

            # remove channels with a regexp filter by channel names
            temp = []
            for ch in plotables:
                bskip = False
                name = str(self.door.macro_server.getElementInfo(ch))
                for reel in self.chfilter:
                    if re.match(reel, name):
                        bskip = True
                        break
                if not bskip:
                    temp.append(ch)

            plotables = temp
            plotables.sort()
            for ch in plotables:
                w = CustomTaurusTrend(parent=self)

                w.setXIsTime(False)
                w.setScanDoor(self.door.name())
                w.setScansXDataKey(axes[0])

                chname = str(self.door.macro_server.getElementInfo(ch))
                w.setTitle(chname)

                # channel name of the haspp02ch2:10000/expchan/vfcadc_eh2a/4 kind
                # pname = u'%s - %s' % (str(ch), ":".join(axes))
                pname = u'%s' % (str(ch))

                panel = self.createPanel(w, pname, registerconfig=False,
                                         permanent=False)

                pw = self.getPanelWidget(pname)
                self._trends1d.append(pname)

                flt = ChannelFilter([ch])
                pw.onScanPlotablesFilterChanged(flt)

                try:  # if the panel is a dockwidget, raise it
                    pw.raise_()
                except:
                    pass

                newpanels.append(pname)

        # remove trends that are no longer configured
        removedpanels = []
        olditems = list(self.panels)
        for name in olditems:
            if name not in newpanels:
                removedpanels.append(name)
                self.removePanel(name)
                try:
                    index = self._trends1d.index(name)
                    w = self._trends1d.pop(index)
                    try:
                        w.deleteLater()
                    except AttributeError:
                        pass
                except ValueError:
                    pass

        removedpanels = []
        return newpanels, removedpanels

    def disconnectScanTrendSetWidgets(self):
        for w in self.panels:
            if isinstance(w, ScanTrendsSet):
                w.disconnectQDoor(self.door.name())

    def createPanel(self, widget, name, **kwargs):
        '''Creates a "panel" from a widget. In this basic implementation this
        means that the widgets is shown as a non-modal top window

        :param widget: (QWidget) widget to be used for the panel
        :param name: (str) name of the panel. Must be unique.

        Note: for backawards compatibility, this implementation accepts
        arbitrary keyword arguments which are just ignored
        '''
        self.info("Creating panel %s %s " % (str(widget), str(name)))
        widget.setWindowTitle(name)
        self.__panels[name] = widget

    def getPanelWidget(self, name):
        '''Returns the widget associated to a panel name

        :param name: (str) name of the panel. KeyError is raised if not found

        :return: (QWidget)
        '''
        return self.__panels[name]

    def showWidgets(self, bflag=True):
        for w in self.__panels.values():
            try:
                if bflag:
                    w.show()
                else:
                    w.hide()
            except AttributeError:
                pass

    def onExpConfChanged(self, expconf):
        self.door = self.getModelObj()
        self.info("Changing experimental configuration")
        DynamicPlotManager.onExpConfChanged(self, expconf)


KEYTT_YMIN, KEYTT_YMAX, KEYTT_CEN, KEYTT_FWHM, KEYTT_LEFTEDGE, \
KEYTT_RIGHTEDGE, KEYTT_XLIMMIN, KEYTT_XLIMMAX, KEYTT_CENMASS = 'TTMIN', 'TTMAX', 'TTCEN', 'TTFWHM', 'LEFTEDGE', 'RIGHTEDGE', 'XLIMMIN', 'XLIMMAX', 'TT_CENMASS'


class CustomTaurusTrend(TaurusTrend, logger.LocalLogger, Checker):
    signdatapicked = QtCore.pyqtSignal(dict)
    signstatcalculated = QtCore.pyqtSignal(TaurusTrend)

    def __init__(self, parent=None, designMode=False, debug_level=None):

        # position pick
        self._positionPicker = None
        self._positionMarker = None


        self._motorMarker = None

        # in order to control when picked points are necessary
        self._report_picked = True

        # in order to have an intrinsic information on the timescan mode
        self._btimescan = False

        # storage for scan statistics
        self.__stats = None
        self._checkStatistics()

        TaurusTrend.__init__(self, parent=None, designMode=False)
        logger.LocalLogger.__init__(self, name=self.__class__.__name__, debug_level=debug_level, parent=parent)
        Checker.__init__(self)

        self.__initCustom()

    @property
    def lastposition(self):
        return self.__last_position

    @lastposition.setter
    def lastposition(self, value):
        self.__last_position = value

    @property
    def prelastposition(self):
        return self.__prelast_position

    @prelastposition.setter
    def prelastposition(self, value):
        self.__prelast_position = value

    @property
    def lastindex(self):
        return self.__last_picked_index

    @lastindex.setter
    def lastindex(self, value):
        """
        Last picked point position - does not matter if point or position else
        :param value: QPointF
        :return:
        """
        self.__last_picked_index = value

    def _resetStatistics(self):
        """
        Resets statistics object
        :return:
        """
        self.__stats = {}

        for k in (KEYTT_YMIN, KEYTT_YMAX, KEYTT_CEN, KEYTT_FWHM, KEYTT_LEFTEDGE, KEYTT_RIGHTEDGE, KEYTT_XLIMMIN, KEYTT_XLIMMAX, KEYTT_CENMASS):
            self.__stats[k] = None

    def _setStatistics(self, key, value):
        """
        Sets a specified key of the statistics object
        :param key: str() or unicode()
        :param value: QPointF() or int()
        :return:
        """
        self.__stats[key] = value

    def _getStatistics(self, key):
        """
        Sets a specified key of the statistics object
        :param key: str() or unicode()
        :param value: QPointF() or int()
        :return:
        """
        return self.__stats[key]

    def _checkStatistics(self):
        """
        Tests statisticsdictionary and initializes it
        :return:
        """
        res = True
        if self.__stats is None or len(self.__stats.keys()) == 0:
            self._resetStatistics()
            res = False

        # statistics is not full if some of the keys are not calculated
        if res:
            for v in self.__stats.values():
                if v is None:
                    res = False
                break
        return res

    def pickDataPoint(self, pos, scope=20, showMarker=True, targetCurveNames=None):
        res = self.__pickDataPoint(pos, scope=scope, showMarker=showMarker, targetCurveNames=targetCurveNames)

        if res is None:
            return

        point, index = None, None

        try:
            point, index = res[KEY_POINT], res[KEY_INDEX]
        except AttributeError, KeyError:
            return

        self.lastindex = index

        self.__reportPicked(point=res[KEY_POINT], curvname=res[KEY_CURVNAME], index=res[KEY_INDEX], cmd=res[KEY_CMD])

    def controlReportPicked(self, bflag):
        if bflag is not None and isinstance(bflag, bool):
            self._report_picked = bflag

    def setTimescanMode(self, bflag):
        if bflag is not None and isinstance(bflag, bool):
            self._btimescan = bflag

    def registerPick(self, func):
        self.signdatapicked.connect(func)

    def registerStatCalculated(self, func):
        self.signstatcalculated.connect(func)

    def reportStatCalculated(self):
        self.signstatcalculated.emit(self)

    def _adjustPointMarkerLabel(self):
        """
        Adjusts default label for the marker
        :return:
        """
        label = self._pickedMarker.label()

        pen = QtGui.QPen()
        pen.setColor(WHITE)
        pen.setWidth(5)

        brush = QtGui.QBrush()
        brush.setColor(WHITE)
        brush.setStyle(Qt.Qt.SolidPattern)

        label.setBackgroundBrush(brush)
        label.setColor(BLACK)
        label.setBackgroundPen(pen)

        self._pickedMarker.setLabel(label)

    def _canvasContextMenu(self):
        """Returns a contextMenu for the canvas

        :return: (Qt.QMenu) the context menu for the canvas
        """

        menu = Qt.QMenu(self)

        scalesSubMenu = menu.addMenu("&Scales")
        scalesSubMenu.addAction(self._autoscaleAllAxisAction)
        for axis in (Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight):
            if self.axisEnabled(axis):
                scalesSubMenu.addMenu(self._axisContextMenu(axis=axis))
        menu.addSeparator()

        # group for selection of modes
        ag = Qt.QActionGroup(menu)
        ag.addAction(self._positionPickedAction)
        ag.addAction(self._dataInspectorAction)
        ag.addAction(self._zoomerAction)
        ag.setExclusive(True)
        self.connect(ag, QtCore.SIGNAL("triggered (QAction *)"), self._actionTracker)

        # group for calculations
        agcalc = Qt.QActionGroup(menu)
        agcalc.addAction(self._findCenterDerivative)
        agcalc.addAction(self._findCenterDerivativeNoisy)
        agcalc.setExclusive(True)
        self.connect(agcalc, QtCore.SIGNAL("triggered (QAction *)"), self._actionTracker)
        
        # group for center of mass
        agcms = Qt.QActionGroup(menu)
        agcms.addAction(self._findCenterCMS)
        agcms.addAction(self._findCenterNegativeCMS)
        agcms.setExclusive(True)
        self.connect(agcms, QtCore.SIGNAL("triggered (QAction *)"), self._actionTracker)

        menu.addAction(self._positionPickedAction)
        menu.addAction(self._dataInspectorAction)
        menu.addAction(self._zoomerAction)
        menu.addAction(self._clearMarkersAction)

        # statistics related things
        if self._checkStatistics():
            menu.addSeparator()
            menu.addAction(self._findCenterBetweenClicks)
            menu.addSeparator()
            menu.addAction(self._findCenterDerivative)
            menu.addAction(self._findCenterDerivativeNoisy)
            menu.addAction(self._findCenterCMS)
            menu.addAction(self._findCenterNegativeCMS)
            menu.addSeparator()
            menu.addAction(self._findYMaximum)
            menu.addAction(self._findYMinimum)
            menu.addAction(self._findXMaximum)
            menu.addAction(self._findXMinimum)

            menu.addSeparator()
            menu.addAction(self._findXLeftEdge)
            menu.addAction(self._findXRightEdge)

            menu.addSeparator()

        if self.check(self._getStatistics(KEYTT_FWHM), float):
            menu.addSeparator()
            menu.addAction('FWHM - %6.4f' % self._getStatistics(KEYTT_FWHM))
            menu.addAction('CENTER - %6.4f' % self._getStatistics(KEYTT_CEN).x())
            menu.addAction('CMS - %6.4f' % self._getStatistics(KEYTT_CENMASS).x())

        menu.addSeparator()
        exportSubMenu = menu.addMenu("&Export && Print")
        menu.addAction(self._curveStatsAction)
        exportSubMenu.addAction(self._printAction)
        exportSubMenu.addAction(self._exportPdfAction)
        exportSubMenu.addAction(self._exportAsciiAction)

        menu.addSeparator()

        if self.isWindow():
            menu.addAction(self._closeWindowAction)

        return menu

    def __initCustom(self):
        # initialize trackers
        self.__initTrackers()

        # initialize actions
        self.__initCustomActions()

    def __initCustomActions(self):
        """
        Create custom actions for our specific task
        """
        self._setActionShortcut(self._autoscaleAllAxisAction, SHORTCUT_AUTOSCALE)

        # navigating through the points - LEFT, RIGHT
        self._nextPickedAction = Qt.QAction("Next point", None)
        self._prepareAction(self._nextPickedAction, SHORTCUT_MOVERIGHT, lambda: self.moveTracker(direction=1))

        self._previousPickedAction = Qt.QAction("Previous point", None)
        self._prepareAction(self._previousPickedAction, SHORTCUT_MOVELEFT, lambda: self.moveTracker(direction=-1))

        # navigating through the points - LEFT, RIGHT
        self._nextPickedActionJump = Qt.QAction("Jump 10 steps", None)
        self._prepareAction(self._nextPickedActionJump, SHORTCUT_JUMPRIGHT, lambda: self.moveTracker(direction=1, step=10.))

        self._previousPickedActionJump = Qt.QAction("Jump -10 steps", None)
        self._prepareAction(self._previousPickedActionJump, SHORTCUT_JUMPLEFT, lambda: self.moveTracker(direction=-1, step=10.))

        # setting new action for position determination
        self._positionPickedAction = Qt.QAction("Position", None)
        self._prepareAction(self._positionPickedAction, SHORTCUT_TOGGLEPOSITION, lambda: self._actionTracker(self._positionPickedAction), bcheckable=True, bchecked=True)

        # modification of the default action for point inspection
        self._dataInspectorAction = Qt.QAction("Data &Inspector mode", None)
        self._prepareAction(self._dataInspectorAction, SHORTCUT_TOGGLEPOINT, lambda: self._actionTracker(self._dataInspectorAction), bcheckable=True, bchecked=False)

        # setting up zoom action
        self._zoomerAction = Qt.QAction("Zoom", None)
        self._prepareAction(self._zoomerAction, SHORTCUT_TOGGLEZOOM, lambda: self._actionTracker(self._zoomerAction), bcheckable=True, bchecked=False)

        # clear all markers
        self._clearMarkersAction = Qt.QAction("Clear Markers", None)
        self._prepareAction(self._clearMarkersAction, SHORTCUT_CLEARMARKER, self.cleanupScan)

        # action for peak position determination
        self._findYMaximum = Qt.QAction("Find Y Maximum", None)
        self._prepareAction(self._findYMaximum, SHORTCUT_YMAX, self._findDataYMaximum)

        # action for peak position determination
        self._findYMinimum = Qt.QAction("Find Y Minimum", None)
        self._prepareAction(self._findYMinimum, SHORTCUT_YMIN, self._findDataYMinimum)

        # action for X axis jump - x maximum
        self._findXMaximum = Qt.QAction("Find X Maximum", None)
        self._prepareAction(self._findXMaximum, SHORTCUT_XMAX, self._findDataXMaximum)

        # action for X axis jump - x minimum
        self._findXMinimum = Qt.QAction("Find X Minimum", None)
        self._prepareAction(self._findXMinimum, SHORTCUT_XMIN, self._findDataXMinimum)

        # action for edge finding - left
        self._findXLeftEdge = Qt.QAction("Find Left Edge", None)
        self._prepareAction(self._findXLeftEdge, SHORTCUT_XLEFTEDGE, self._findDataXLeftEdge)

        # action for edge finding - right
        self._findXRightEdge = Qt.QAction("Find Right Edge", None)
        self._prepareAction(self._findXRightEdge, SHORTCUT_XRIGHTEDGE, self._findDataXRightEdge)

        # action for peak position determination
        self._findCenterDerivative = Qt.QAction("Find center (derivative - by region)", None)
        self._prepareAction(self._findCenterDerivative, SHORTCUT_CENTERDERIVATIVE, lambda a=self._findCenterDerivative: self._findDataCenterDerivative(action=a), bcheckable=True, bchecked=True)

        # action for peak position determination
        self._findCenterDerivativeNoisy = Qt.QAction("Find center (derivative - by points)", None)
        self._prepareAction(self._findCenterDerivativeNoisy, SHORTCUT_CENTERDERIVATIVENOISY, lambda a=self._findCenterDerivativeNoisy: self._findDataCenterDerivative(action=a), bcheckable=True, bchecked=False)

        # action for peak position determination
        self._findCenterCMS = Qt.QAction("Find center (CoM)", None)
        self._prepareAction(self._findCenterCMS, SHORTCUT_CENTERCMS, lambda a=self._findCenterCMS: self._findDataCenterMass(action=a), bcheckable=True, bchecked=True)

        # action for peak position determination
        self._findCenterNegativeCMS = Qt.QAction("Find center (negative CoM)", None)
        self._prepareAction(self._findCenterNegativeCMS, SHORTCUT_CENTERNEGATIVECMS, lambda a=self._findCenterNegativeCMS: self._findDataCenterMass(action=a), bcheckable=True, bchecked=False)

        # action for determination of center between two clicks
        self._findCenterBetweenClicks = Qt.QAction("Find center (between two last clicks)", None)
        self._prepareAction(self._findCenterBetweenClicks, SHORTCUT_CENTERBETWEENCLICKS, self._findCenterClicks)

        # installing actions
        for action in (self._autoscaleAllAxisAction, self._nextPickedAction, self._previousPickedAction,
                       self._positionPickedAction, self._zoomerAction, self._dataInspectorAction,
                       self._clearMarkersAction, self._findYMaximum, self._findYMinimum, self._findCenterDerivative,
                       self._findCenterDerivativeNoisy,
                       self._findXMinimum, self._findXMaximum, self._findXRightEdge, self._findXLeftEdge,
                       self._nextPickedActionJump, self._previousPickedActionJump, self._findCenterCMS, self._findCenterBetweenClicks, self._findCenterNegativeCMS):
            action.setShortcutContext(Qt.Qt.WidgetShortcut)
            self.canvas().addAction(action)

        # setting the default behavior
        self._actionTracker(self._positionPickedAction)

    def _setActionShortcut(self, action, shortcut):
        """
        Sets shortcuts based on action and type of shortcur
        :param action: QAction
        :param shortcut: list() or int()
        :return:
        """
        if self.check(action, Qt.QAction) and self.check(shortcut):
            if self.check(shortcut, list) or self.check(shortcut, tuple):
                action.setShortcuts(shortcut)
            else:
                action.setShortcut(shortcut)

    def _prepareAction(self, action, shortcut, func, bcheckable=False, bchecked=None):
        """
        Optimization to save space - prepares action
        :param action:
        :param shortcut:
        :param func:
        :param bcheckable:
        :param bchecked:
        :return:
        """
        self._setActionShortcut(action, shortcut)
        if bcheckable is not None:
            action.setCheckable(bcheckable)
        if bchecked is not None:
            action.setChecked(bchecked)

        self.connect(action, QtCore.SIGNAL("triggered()"), func)


    def __initTrackers(self):
        # custom picked point
        self.__prelast_position = None
        self.__last_position = None
        self.__last_picked_index = None

        # position related marker and the picker
        self._positionMode = False
        self._positionMarker = self.__getPositionMarker()

        self._positionPicker = Qwt5.QwtPicker(self.canvas())
        self._positionPicker.setSelectionFlags(Qwt5.QwtPicker.PointSelection)
        self._positionPicker.setEnabled(False)

        self.connect(self._positionPicker, Qt.SIGNAL('selected(QwtPolygon)'), self.__pickPosition)

        self._zoomMode = False

    def setPositionMarker(self, marker):
        if self.check(marker, Qwt5.QwtPlotMarker):
            self._positionMarker = marker

    def setMotorMarker(self, marker):
        if self.check(marker, VerticalMarker):
            self._motorMarker = VerticalMarker(lColor=marker.color, lWidth=marker.lwidth, lStyle=marker.style)
            self._motorMarker.attach(self)

    def setPointMarker(self, marker):
        if self.check(marker, Qwt5.QwtPlotMarker):
            self._pickedMarker = marker

            if isinstance(marker, Qwt5.QwtPlotMarker):
                self._adjustPointMarkerLabel()

    def __togglePickerCursor(self, bflag=False):
        if bflag:
            cursor = Qt.Qt.PointingHandCursor
        else:
            cursor = Qt.Qt.CrossCursor

        self.canvas().setCursor(cursor)

    def toggleDataInspectorMode(self, bflag=None):
        """
        Enables/Disables the Inspector Mode.
        """
        self.debug("Toggling Data Inspector Mode")

        self.__togglePickerCursor(True)

        self._cleanupMarkers()
        self._cleanupTrackers()

        self.replot()

        self._pointPicker.setEnabled(True)

        self._inspectorMode = True

        return self._inspectorMode

    def setMotorMarkerPosition(self, value):
        """
        Sets horizontal position of the motor marker
        :param value: float() - position
        :return:
        """
        pos = None
        try:
            pos = float(value)
        except:
            pass

        if self.check(pos, float):
            self._motorMarker.attach(self)
            self._motorMarker.setXValue(value)
            self.autoScaleAllAxes()
            self.replot()

    def togglePositionMode(self):
        """
        Enables disables tracker responsible for arbitary position information
        :return:
        """
        self.debug("Toggling Position Determination Mode")
        self.__togglePickerCursor(True)

        self._cleanupMarkers()
        self._cleanupTrackers()

        self.replot()

        self._positionPicker.setEnabled(True)

        self._positionMode = True

        return self._positionMode

    def toggleZoomMode(self):
        """
        Enables/Disables Zooming mode
        :return:
        """
        self.debug("Toggling Zoomer mode")
        self.__togglePickerCursor(False)

        self._cleanupMarkers()
        self._cleanupTrackers()

        self.replot()

        self._zoomer.setEnabled(True)

        self._zoomMode = True

        self._allowZoomers = True

        return self._zoomMode

    def _cleanupMarkers(self, bkeepstate=False):
        """
        Cleans up all markers, information
        :param bkeepstate: bool() controls if we want to reset flags representing which mode is use
        :return:
        """
        for marker in (self._pickedMarker, self._positionMarker):
            if marker is not None:
                marker.detach()

        if self._btimescan:
            self._motorMarker.detach()

        self.__last_position = None
        self.__last_picked_index = None

        if not bkeepstate:
            self._positionMode = False
            self._inspectorMode = False
            self._zoomMode = False

        self.replot()

    def cleanupScan(self):
        self._cleanupMarkers(bkeepstate=True)

    def calculatePlotStatistics(self):
        """
        Calculates plot statistics - peaks, center, FWHM
        :return:
        """
        self._resetStatistics()

        xmin, xlimmin, xmax, xlimmax, ymin, ymax, xcen, xcencms = None, None, None, None, None, None, None, None

        # find minimum and maximum values
        for cname in self.getCurveNames():
            curve = self.getCurve(cname)

            if curve.dataSize() > 0:
                ymax = curve.maxYValue()
                ymin = curve.minYValue()

                xlimmin = curve.minXValue()
                xlimmax = curve.maxXValue()

                for i in range(curve.dataSize()):
                    if curve.y(i) == ymax:
                        xmax = float(curve.x(i))
                    if curve.y(i) == ymin:
                        xmin = float(curve.x(i))

                    if self.check(xmin) and self.check(xmax):
                        break
            break

        # do nothing if we have no data
        if not self.check(ymin) or not self.check(ymax):
            return

        # all data
        x, y = list(curve.data().xData()), list(curve.data().yData())

        # minor corrections for calculations near edges
        x.append(x[-1])
        y.append(y[-1])

        x.insert(0, x[0])
        y.insert(0, y[0])
        

        # calculate derivative - take data in the current view
        map = self.canvasMap(Qwt5.QwtPlot.xBottom)
        mi, ma = map.s1(), map.s2()

        tx, ty = [], []

        # get only points available in the view
        for (i, pos) in enumerate(x):
            if mi <= pos <=ma:
                tx.append(pos)
                ty.append(y[i])

        if len(tx) < 2:
            return

        # transforming into a np world
        tx, ty = np.array(tx), np.array(ty)

        cimin, cimax = min(tx), max(tx)
        if self._findCenterDerivative.isChecked():
            cimin, cimax = self._calcDerivative(tx, ty)
        else:
            cimin, cimax = self._calcPureDerivative(tx, ty)

        # center according to the derivative
        xcen = (cimax + cimin) / 2

        # center of mass
        xcencms = 0.
        if self._findCenterCMS.isChecked():
            xcencms = self._calcCMS(tx, ty)
        else:
            xcencms = self._calcNegativeCMS(tx, ty)

        # FWHM
        fwhm = abs(cimax - cimin)

        # sets storage with data
        if not self.check(xmax) or not self.check(ymax):
            return

        self._setStatistics(KEYTT_YMIN, QtCore.QPointF(xmin, ymin))
        self._setStatistics(KEYTT_YMAX, QtCore.QPointF(xmax, ymax))
        self._setStatistics(KEYTT_CEN, QtCore.QPointF(xcen, ymax))
        self._setStatistics(KEYTT_XLIMMIN, QtCore.QPointF(xlimmin, ymax))
        self._setStatistics(KEYTT_XLIMMAX, QtCore.QPointF(xlimmax, ymax))

        self._setStatistics(KEYTT_FWHM, fwhm)
        self._setStatistics(KEYTT_LEFTEDGE, QtCore.QPointF(min(cimin, cimax), ymax))
        self._setStatistics(KEYTT_RIGHTEDGE, QtCore.QPointF(max(cimin, cimax), ymax))

        self._setStatistics(KEYTT_CENMASS,  QtCore.QPointF(xcencms, ymax))

    def _calcCMS(self, x, y):
        """
        Calculates a center of mass
        :param x:
        :param y:
        :return:
        """
        summass = 0.
        totalsum = 0.

        x, y = np.array(x), np.array(y)
        # must be an numpy array - invert shape
        y = (y-(y[0]+y[-1])/2)

        for (i, value) in enumerate(x):
            summass += y[i]
            totalsum += x[i]*y[i]

        if summass == 0:
            res = (max(x)+min(x))/2
        else:
            res = totalsum/summass
        return res

    def _calcNegativeCMS(self, x, y):
        """
        Calculates a center of mass
        :param x:
        :param y:
        :return:
        """
        summass = 0.
        totalsum = 0.

        x, y = np.array(x), np.array(y)
        # must be an numpy array - invert shape
        y = (y-(y[0]+y[-1])/2)*(-1)

        for (i, value) in enumerate(x):
            summass += y[i]
            totalsum += x[i]*y[i]

        if summass == 0:
            res = (max(x)+min(x))/2
        else:
            res = totalsum/summass
        return res


    def _calcDerivative(self, x, y):
        """
        Calculates a derivative and goes to the center of mass of maxima and minima values
        :return:
        """
        leftedge, rightedge = min(x), max(x)

        cx, cy = np.diff(np.array([x, y]))
        cx = np.resize(x, (len(x) - 1))

        # find indexes of maximum and minimums in a derivative
        func_pos, func_neg = self._calcCMS, self._calcNegativeCMS
        try:
            rightedge = (cx[cy.argmax()]+cx[cy.argmax()+1])/2.
        except IndexError:
            rightedge = cx[cy.argmax()]

        try:
            leftedge = (cx[cy.argmin()]+cx[cy.argmin()+1])/2.
        except IndexError:
            leftedge = cx[cy.argmin()]

        posx, posy, negx, negy = [], [], [], []

        posx, posy = cx[rightedge-5:rightedge+5], cy[rightedge-5:rightedge+5]
        negx, negy = cx[leftedge-5:leftedge+5], cy[leftedge-5:leftedge+5]

        if len(posx)!=len(posy) or len(negx)!=len(negy) or len(posx)==0 or len(negx)==0:
            func_pos = func_neg = None

        # find indexes of maximum and minimums in a derivative
        if func_pos is not None:
            leftedge = func_pos(posx, posy)
        if func_neg is not None:
            rightedge = func_neg(negx, negy)

        leftedge, rightedge = min(leftedge, rightedge), max(leftedge, rightedge)

        return leftedge, rightedge

    def _calcPureDerivative(self, x, y):
        """
        Calculates a derivative and goes to the center of mass of positive and negative values
        :return:
        """
        leftedge, rightedge = min(x), max(x)

        cx, cy = np.diff(np.array([x, y]))
        cx = np.resize(x, (len(x) - 1))

        # find indexes of maximum and minimums in a derivative
        try:
            rightedge = (cx[cy.argmax()]+cx[cy.argmax()+1])/2.
        except IndexError:
            rightedge = cx[cy.argmax()]

        try:
            leftedge = (cx[cy.argmin()]+cx[cy.argmin()+1])/2.
        except IndexError:
            leftedge = cx[cy.argmin()]

        return leftedge, rightedge



    def _findDataYMaximum(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, searches for a peak, puts the position marker to its position
        :return:
        """
        self._findStatisticsPosition(KEYTT_YMAX, breplot=breplot, brecalculate=brecalculate)

    def _findDataYMinimum(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, searches for a negative peak, puts the position marker to its position
        :return:
        """
        self._findStatisticsPosition(KEYTT_YMIN, breplot=breplot, brecalculate=brecalculate)


    def _findDataXMaximum(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, limit of x scan position - maximum
        :return:
        """
        self._findStatisticsPosition(KEYTT_XLIMMAX, breplot=breplot, brecalculate=brecalculate)

    def _findDataXMinimum(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, limit of x scan position - minimum
        :return:
        """
        self._findStatisticsPosition(KEYTT_XLIMMIN, breplot=breplot, brecalculate=brecalculate)

    def _findDataXLeftEdge(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, limit of x scan position - maximum
        :return:
        """
        self._findStatisticsPosition(KEYTT_LEFTEDGE, breplot=breplot, brecalculate=True)

    def _findDataXRightEdge(self, breplot=True, brecalculate=False):
        """
        Processes data in the current window, limit of x scan position - minimum
        :return:
        """
        self._findStatisticsPosition(KEYTT_RIGHTEDGE, breplot=breplot, brecalculate=True)

    def _findDataCenterDerivative(self, breplot=True, brecalculate=True, action=None):
        """
        Processes data in the current window, searches for a negative peak, puts the position marker to its position
        :return:
        """
        # uncheck all relevant actions, check
        for act in (self._findCenterDerivative, self._findCenterDerivativeNoisy):
            act.setChecked(False)
        if action is not None:
            action.setChecked(True)

        self._findStatisticsPosition(KEYTT_CEN, breplot=breplot, brecalculate=brecalculate)

    def _findDataCenterMass(self, breplot=True, brecalculate=True, action=None):
        """
        Processes data in the current window, searches for a negative peak, puts the position marker to its position
        :return:
        """
        # uncheck all relevant actions, check
        for act in (self._findCenterCMS, self._findCenterNegativeCMS):
            act.setChecked(False)
        if action is not None:
            action.setChecked(True)

        self._findStatisticsPosition(KEYTT_CENMASS, breplot=breplot, brecalculate=brecalculate)

    def _findCenterClicks(self):
        """
        Processes data in the current window, searches for a negative peak, puts the position marker to its position
        :return:
        """
        if self.check(self.prelastposition) and self.check(self.lastposition):
            pos = (self.lastposition+self.prelastposition)/2
            self.setPositionMarkerValue(pos.x(), pos.y())
            self.__reportPicked(pos)

    def _findStatisticsPosition(self, key, breplot=True, brecalculate=False):
        """
        Uses a key to find a proper entry in self.__stats and the corresponding position
        :param key: str()
        :param breplot: bool()
        :param brecalculate: bool()
        :return:
        """
        if not self._checkStatistics() or brecalculate:
            self.calculatePlotStatistics()

        # get calculated data
        point = self._getStatistics(key)

        if breplot and self.check(point, QtCore.QPointF):
            self._cleanupMarkers()
            self._actionTracker(self._positionPickedAction)
            self.setPositionMarkerValue(point.x(), point.y())
            self.__reportPicked(point)

        self.reportStatCalculated()


    def setPositionMarkerValue(self, x, y):
        """
        Sets current value of the position marker - attaches it to the plot
        :param value:
        :return:
        """
        self._positionMarker.setXValue(x)
        self._positionMarker.attach(self)
        self.__last_position = QtCore.QPointF(x, y)

        self.replot()


    def _cleanupTrackers(self):
        """
        Disables trackers
        :return:
        """
        for el in (self._positionPicker, self._zoomer, self._pointPicker):
            try:
                el.setEnabled(False)
            except AttributeError:
                pass

        self._allowZoomers = False


    def autoScaleAllAxes(self):
        '''Optimized autoscale of whole plot'''
        minX=float('inf')
        maxX=float('-inf')
        if self.getXDynScale():
            originalXRange = self.getXAxisRange()
            self.curves_lock.acquire()
            try:
                for c in self.curves.values():
                    if c.minXValue() < minX:
                        minX = c.minXValue()
                    if c.maxXValue() > maxX:
                        maxX = c.maxXValue()
                    if minX!=maxX:
                        break
            finally:
                self.curves_lock.release()

        # show motor position and avoid timescan
        if not self._btimescan:
            minX = min(minX, self._motorMarker.xValue())
            maxX = max(maxX, self._motorMarker.xValue())

        for axis in range(Qwt5.QwtPlot.axisCnt):
            if axis == Qwt5.QwtPlot.xBottom and minX==maxX:
                Qwt5.QwtPlot.setAxisScale(self, axis, minX-0.5*originalXRange, minX+0.5*originalXRange)
            elif axis == Qwt5.QwtPlot.xBottom:
                Qwt5.QwtPlot.setAxisScale(self, axis, minX, maxX)
            else:
                Qwt5.QwtPlot.setAxisAutoScale(self, axis)
        self.replot()
        #Update the zoom stacks
        self._zoomer1.setZoomBase()
        self._zoomer2.setZoomBase()

    def __pickDataPoint(self, pos, scope=20, showMarker=True, targetCurveNames=None):
        """
        Finds the pyxel-wise closest data point to the given position. The
        valid search space is constrained by the scope and targetCurveNames
        parameters.

        :param pos: (Qt.QPoint or Qt.QPolygon) the position around which to look
                    for a data point. The position should be passed as a
                    Qt.QPoint (if a Qt.QPolygon is given, the first point of the
                    polygon is used). The position is expected in pixel units,
                    with (0,0) being the top-left corner of the plot
                    canvas.

        :param scope: (int) defines the area around the given position to be
                      considered when searching for data points. A data point is
                      considered within scope if its manhattan distance to
                      position (in pixels) is less than the value of the scope
                      parameter. (default=20)

        :param showMarker: (bool) If True, a marker will be put on the picked
                           data point. (default=True)

        :param targetCurveNames: (sequence<str>) the names of the curves to be
                                 searched. If None passed, all curves will be
                                 searched

        :return: (tuple<Qt.QPointF,str,int> or tuple<None,None,None>) if a point
                 was picked within the scope, it returns a tuple containing the
                 picked point (as a Qt.QPointF), the curve name and the index of
                 the picked point in the curve data. If no point was found
                 within the scope, it returns None,None,None
        """
        self.info("Tracking data point")

        if isinstance(pos, Qt.QPolygon): pos = pos.first()
        scopeRect = Qt.QRect(-scope, -self.canvas().height(), scope, 2 * self.canvas().height())

        scopeRect.moveCenter(pos)
        mindist = scope
        picked = None
        pickedCurveName = None
        pickedIndex = None
        self.curves_lock.acquire()

        try:
            if targetCurveNames is None: targetCurveNames = self.curves.iterkeys()
            for name in targetCurveNames:
                curve = self.curves.get(name, None)
                if curve is None: self.error("Curve '%s' not found" % name)
                if not curve.isVisible(): continue
                data = curve.data()

                found_index = None
                for i in xrange(data.size()):
                    point = Qt.QPoint(self.transform(curve.xAxis(), data.x(i)),
                        self.transform(curve.yAxis(), data.y(i)))
                    if scopeRect.contains(point):
                        dist = abs(pos.x() - point.x())
                        if dist < mindist:
                            found_index = i
                            mindist = dist
                if found_index is not None:
                    picked = Qt.QPointF(data.x(found_index), data.y(found_index))
                    pickedCurveName = name
                    pickedIndex = found_index
                    pickedAxes = curve.xAxis(), curve.yAxis()
        finally:
            self.curves_lock.release()

        if showMarker and picked is not None:
            self._pickedMarker.detach()
            self._pickedMarker.setValue(picked)
            self._pickedMarker.setAxis(*pickedAxes)
            self._pickedMarker.attach(self)
            self._pickedCurveName = pickedCurveName
            self._pickedMarker.pickedIndex = pickedIndex

            pickedCurveTitle = self.getCurveTitle(pickedCurveName)

            self.replot()
            label = self._pickedMarker.label()

            if self.getXIsTime():
                infotxt = "'%s'[%i]:\n\t (t=%s, y=%.5g)" % (
                    pickedCurveTitle, pickedIndex, datetime.fromtimestamp(picked.x()).ctime(), picked.y())
            else:
                infotxt = "[%i]:(%.5g;%.5g)" % (pickedIndex, picked.x(), picked.y())

            label.setText(infotxt)
            fits = label.textSize().width() < self.size().width()
            if fits:
                self._pickedMarker.setLabel(Qwt5.QwtText(label))
                self.alignLabel(self._pickedMarker)
                self.replot()
            else:
                popup = Qt.QWidget(self, Qt.Qt.Popup)
                popup.setLayout(Qt.QVBoxLayout())
                popup.layout().addWidget(Qt.QLabel(infotxt))  # @todo: make the widget background semitransparent green!
                popup.setWindowOpacity(self._pickedMarker.labelOpacity)
                popup.show()
                popup.move(self.pos().x() - popup.size().width(), self.pos().y())
                popup.move(self.pos())
                Qt.QTimer.singleShot(5000, popup.hide)

        return self.__prepPickedDict(point=picked, curvname=pickedCurveName, index=pickedIndex, cmd=CMD_POINT)

    def alignLabel(self, marker):
        '''Sets the label alignment in a "smart" way (depending on the current
        marker's position in the canvas).
        '''
        xmap = marker.plot().canvasMap(marker.xAxis())
        ymap = marker.plot().canvasMap(marker.yAxis())
        xmiddlepoint = xmap.p1() + xmap.pDist() / 2  # p1,p2 are left,right here
        ymiddlepoint = ymap.p2() + ymap.pDist() / 2  # p1,p2 are bottom,top here (and pixel coords start from top!)
        xPaintPos = xmap.transform(marker.xValue())
        yPaintPos = ymap.transform(marker.yValue())

        if xPaintPos > xmiddlepoint:  # the point in the right side
            hAlign = Qt.Qt.AlignLeft
        else:
            hAlign = Qt.Qt.AlignRight

        if yPaintPos > ymiddlepoint:  # the point is in the bottom side
            vAlign = Qt.Qt.AlignTop
        else:
            vAlign = Qt.Qt.AlignBottom

        marker.setLabelAlignment(hAlign | vAlign)

    def __pickPosition(self, pos):
        """
        Picks up any position and reports it back to the agent involved
        :param pos: QRect() - position transformed into graph point
        :return:
        """
        position = pos.first()
        self._positionMarker.detach()

        smx, smy = self.canvasMap(Qwt5.Qwt.QwtPlot.xBottom), self.canvasMap(Qwt5.Qwt.QwtPlot.yLeft)
        x, y = smx.invTransform(position.x()), smy.invTransform(position.y())

        curvename = None
        try:
            if len(self.curves.keys()):
                curvename = self.curves.keys()[0]
        except IndexError, AttributeError:
            pass

        self._positionMarker.setXValue(x)
        self._positionMarker.attach(self)

        self.replot()

        point = QtCore.QPointF(x, y)

        self.__reportPicked(point=point, curvname=curvename, index=None, cmd=CMD_POSITION)

    def _actionTracker(self, action):
        """
        Function responsible for switching different modes
        :param action: QAction()
        :return:
        """
        trackers = ()

        # differenciate bewtee different actions
        if action in (self._positionPickedAction, self._zoomerAction, self._dataInspectorAction):
            trackers = (self._positionPickedAction, self._zoomerAction, self._dataInspectorAction)
        elif action in (self._findCenterDerivative, self._findCenterDerivativeNoisy):
            trackers = (self._findCenterDerivative, self._findCenterDerivativeNoisy)
        elif action in (self._findCenterCMS, self._findCenterNegativeCMS):
            trackers = (self._findCenterCMS, self._findCenterNegativeCMS)

        if action == self._positionPickedAction:
            self.togglePositionMode()
        elif action == self._zoomerAction:
            self.toggleZoomMode()
        elif action == self._dataInspectorAction:
            self.toggleDataInspectorMode()

        self.__checkSpecificTrackerAction(action, trackers)
        action.setChecked(True)

    def __checkSpecificTrackerAction(self, action, trackers):
        """
        Function setting flags indicating which operation modes is used now
        :param action:
        :return:
        """
        for el in trackers:
            if el == action:
                el.setChecked(True)
            else:
                el.setChecked(False)

    def __getPositionMarker(self):
        """
        Function preparing vertical line marker
        :return:
        """
        m = Qwt5.Qwt.QwtPlotMarker()

        m.setLineStyle(Qwt5.Qwt.QwtPlotMarker.VLine)
        m.setXValue(-9999)

        pen = Qt.QPen(Qt.Qt.DashLine)
        pen.setWidth(1)
        m.setLinePen(pen)
        return m

    def moveTracker(self, direction=1, step=None):
        """
        If tracker is present and visible it moves position of the tracker to the next point
        :param direction: int() - can be positive or negative
        :return:
        """
        # different scenarios - point was picked or x position was picked
        if self._positionMode:
            self.__movePosition(direction=direction, step=step)
        elif self._inspectorMode and self.lastindex is not None:
            self.__moveDataPoint(direction=direction)

    def __movePosition(self, direction=1, step=2):
        """
        Move vertical line position within the graph
        :param direction: int() - direction to follow
        :param step: int() - step size in pixels to make
        :return:
        """
        if step is None:
            step = 2

        if self.__last_position is not None:
            pos = self.__last_position

            smx = self.canvasMap(Qwt5.Qwt.QwtPlot.xBottom)

            x = smx.transform(pos.x()) + step * direction
            x = smx.invTransform(x)

            if smx.s1() < x < smx.s2():
                point = Qt.QPointF(x, pos.y())

                self._positionMarker.setXValue(x)
                self.replot()

                self.__reportPicked(point=point, cmd=CMD_POSITION)

    def __moveDataPoint(self, direction=1, step=1):
        """
        Move within scan points by means of curve moints index
        :param direction: int() - direction to move
        :param step: int() - step to move
        :return:
        """
        if self.__last_picked_index is not None:
            self.curves_lock.acquire()

            index = self.__last_picked_index

            try:
                targetCurveNames = self.curves.iterkeys()
                # name looks like haspp02ch2:10000/expchan/vfcadc_eh2a/4 - can embed filter on that
                for name in targetCurveNames:
                    curve = self.curves.get(name, None)
                    next_index = index + direction * step

                    if 0 <= next_index < curve.data().size():
                        point = Qt.QPointF(curve.data().x(next_index), curve.data().y(next_index))

                        self._pickedMarker.detach()
                        self._pickedMarker.setValue(point)
                        self._pickedMarker.attach(self)
                        self._pickedMarker.pickedIndex = next_index

                        self.replot()
                        label = self._pickedMarker.label()

                        if self.getXIsTime():
                            infotxt = "[%i]:\n\t (t=%s, y=%.5g)" % (
                                next_index, datetime.fromtimestamp(point.x()).ctime(), point.y())
                        else:
                            infotxt = "[%i]:(%.5g, %.5g)" % (next_index, point.x(), point.y())

                        label.setText(infotxt)
                        fits = label.textSize().width() < self.size().width()
                        if fits:
                            self._pickedMarker.setLabel(Qwt5.QwtText(label))
                            self.alignLabel(self._pickedMarker)
                            self.replot()
                        else:
                            popup = Qt.QWidget(self, Qt.Qt.Popup)
                            popup.setLayout(Qt.QVBoxLayout())
                            popup.layout().addWidget(
                                Qt.QLabel(infotxt))  # @todo: make the widget background semitransparent green!
                            popup.setWindowOpacity(self._pickedMarker.labelOpacity)
                            popup.show()
                            popup.move(self.pos().x() - popup.size().width(), self.pos().y())
                            popup.move(self.pos())
                            Qt.QTimer.singleShot(5000, popup.hide)

                        self.lastindex = next_index
                        self.__reportPicked(point=point, curvname=name, index=next_index, cmd=CMD_POINT)
                        break
            finally:
                self.curves_lock.release()

    def __reportPicked(self, point=None, curvname=None, index=None, cmd=None):
        if self._report_picked:

            if self.check(self.lastposition, QtCore.QPointF):
                self.prelastposition = QtCore.QPointF(self.lastposition.x(), self.lastposition.y())
            self.lastposition = point

            self.signdatapicked.emit(
                self.__prepPickedDict(point=point, curvname=curvname, index=index, cmd=cmd))

    def __prepPickedDict(self, point=None, curvname=None, index=None, cmd=None):
        """
        Prepares dictionary with picked point information
        :param point:
        :param curvname:
        :param index:
        :param cmd:
        :return:
        """
        return {KEY_POINT: point, KEY_CURVNAME: curvname, KEY_INDEX: index, KEY_CMD: cmd}

    def updateCurves(self, names):
        '''Defines the curves that need to be plotted. For a TaurusTrend, the
        models can refer to:

        - PyTango.SCALARS: they are to be plotted in a trend
        - PyTango.SPECTRUM: each element of the spectrum is considered
          independently

        Note that passing an attribute for X values makes no sense in this case

        Internally, every curve is grouped in a TaurusTrendSet. For each SPECTRUM
        attribute, a TrendSet is created, containing as many curves as the
        lenght of the spectrum For eacha SCALAR attribute, a TrendSet containing
        just one curve is created.

        :param names: (sequence<str>) a sequence of model names

        .. note:: Adding/removing a model will add/remove a whole set. No
                  sub-set adding/removing is allowed.
                  Still, each curve will be independent regarding its
                  properties, and can be hidden/shown independently.

        .. seealso:: :meth:`TaurusPlot.updateCurves`
        '''
        self.curves_lock.acquire()
        try:
            # For it to work properly, 'names' must be a CaselessList, just as
            # self.trendSets is a CaselessDict
            del_sets = [name for name in self.trendSets.keys() if name not in names]

            # if all trends were removed, reset the color palette
            if len(del_sets) == len(self.trendSets):
                self._curvePens.setCurrentIndex(0)

            # update new/existing trendsets
            for name in names:
                name = str(name)
                if "|" in name: raise ValueError('composed ("X|Y") models are not supported by TaurusTrend')
                # create a new TrendSet if not already there
                if not self.trendSets.has_key(name):
                    matchScan = re.search(r"scan:\/\/(.*)",
                                          name)  #check if the model name is of scan type and provides a door
                    if matchScan:
                        tset = ScanTrendsSet(name, parent=self, autoClear=self.getScansAutoClear(),
                                             xDataKey=self._scansXDataKey)

                        self.__qdoorname = matchScan.group(1)  # the name of the door

                        # custom - do not connect with QDoor - will feed data manually
                        # tset.connectWithQDoor(self.__qdoorname)
                    else:
                        tset = TaurusTrendsSet(name, parent=self)
                        if self._forcedReadingPeriod is not None:
                            tset.setForcedReadingPeriod(self._forcedReadingPeriod)
                    self.trendSets[name] = tset
                    tset.registerDataChanged(self, self.curveDataChanged)
            # Trend Sets to be removed
            for name in del_sets:
                name = str(name)
                tset = self.trendSets.pop(name)
                tset.setModel(None)
                tset.unregisterDataChanged(self, self.curveDataChanged)
                tset.forcedReadingTimer = None
                tset.clearTrends(replot=False)
                matchScan = re.search(r"scan:\/\/(.*)", name)
                if matchScan:
                    olddoorname = matchScan.group(1)
                    tset.disconnectQDoor(olddoorname)
            if del_sets:
                self.autoShowYAxes()

            # legend
            self.showLegend(len(self.curves) > 1, forever=False)
            self.replot()

            # keep the replotting timer active only if there is something to refresh
            if self.isTimerNeeded():
                self.debug('(re)starting the timer (in updateCurves)')
                self._replotTimer.start()
            else:
                if self._replotTimer is not None:
                    self.debug('stopping the timer (in updateCurves)')
                    self._replotTimer.stop()

        finally:
            self.curves_lock.release()


class CustomScanTrendsSet(ScanTrendsSet, logger.LocalLogger):
    def __init__(self, name, parent=None, autoClear=True, xDataKey=None, debug_level=None):

        self.__datadesc = None
        ScanTrendsSet.__init__(self, name, parent=parent, autoClear=autoClear, xDataKey=xDataKey)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        self.__door = None

    def connectWithQDoor(self, qdoor=None):
        """
        connects this ScanTrendsSet to a QDoor - external or not
        :param qdoor: (QDoor or str) either a QDoor instance or the QDoor name
        """
        # we connect external or an internal qdoor object
        if qdoor is not None and not isinstance(qdoor, QDoor):
            if self.__door is not None and isinstance(self.__door, QDoor):
                self.disconnectQDoor()
            self.__door = taurus.Device(qdoor)
        elif qdoor is not None and isinstance(qdoor, QDoor):
            if self.__door is not None and isinstance(self.__door, QDoor):
                self.disconnectQDoor()
            self.__door = qdoor

        if self.__door is not None:
            self.connect(self.__door, Qt.SIGNAL("recordDataUpdated"), self.scanDataReceived)


    def disconnectQDoor(self, qdoor=None):
        """
        disconnects this ScanTrendsSet from a QDoor - we consider only internally saved one
        :param qdoor: (QDoor or str) either a QDoor instance or the QDoor name
        """
        if self.__door is not None and isinstance(self.__door, QDoor):
            qdoor = self.__door

        if qdoor is not None and not isinstance(qdoor, QDoor):
            self.__door = taurus.Device(qdoor)

        self.disconnect(qdoor, Qt.SIGNAL("recordDataUpdated"), self.scanDataReceived)


class CurveAppearanceProperties(object):
    '''An object describing the appearance of a TaurusCurve'''

    def __init__(self, sStyle=None, sSize=None, sWidth=None, sColor=None, sFill=None,
                 lStyle=None, lWidth=None, lColor=None, cStyle=None,
                 yAxis=None, cFill=None, title=None, visible=None):
        """
        Creator of :class:`CurveAppearanceProperties`
        Possible keyword arguments are:
            - sStyle= symbolstyle
            - sSize= int
            - sColor= color
            - sFill= bool
            - lStyle= linestyle
            - lWidth= int
            - lColor= color
            - cStyle= curvestyle
            - cFill= bool
            - yAxis= axis
            - visible = bool
            - title= title

        Where:
            - color is a color that QColor() understands (i.e. a
              Qt.Qt.GlobalColor, a color name, or a Qt.Qcolor)
            - symbolstyle is one of Qwt5.QwtSymbol.Style
            - linestyle is one of Qt.Qt.PenStyle
            - curvestyle is one of Qwt5.QwtPlotCurve.CurveStyle
            - axis is one of Qwt5.QwtPlot.Axis
            - title is something that Qwt5.QwtText() accepts in its constructor
              (i.e. a QwtText, QString or any basestring)
        """
        self.sStyle = sStyle
        self.sSize = sSize
        self.sColor = sColor
        self.sFill = sFill
        self.sWidth = sWidth
        self.lStyle = lStyle
        self.lWidth = lWidth
        self.lColor = lColor
        self.cStyle = cStyle
        self.cFill = cFill
        self.yAxis = yAxis
        self.title = title
        self.visible = visible
        self.propertyList = ["sStyle", "sSize", "sWidth", "sColor", "sFill", "lStyle", "lWidth",
                             "lColor", "cStyle", "cFill", "yAxis", "title", "visible"]

    def _print(self):
        """Just for debug"""
        print "-" * 77
        for k in self.propertyList: print k + "= ", self.__getattribute__(k)
        print "-" * 77

    @staticmethod
    def inConflict_update_a(a, b):
        """This  function can be passed to CurvesAppearance.merge()
        if one wants to update prop1 with prop2 except for those
        attributes of prop2 that are set to None"""
        if b is None:
            return a
        else:
            return b

    @staticmethod
    def inConflict_none(a, b):
        """In case of conflict, returns None"""
        return None

    def conflictsWith(self, other, strict=True):
        """returns a list of attribute names that are in conflict between this self and other"""
        result = []
        for aname in self.propertyList:
            vself = getattr(self, aname)
            vother = getattr(other, aname)
            if (vself != vother) and (strict or not (vself is None or vother is None)):
                result.append(aname)
        return result

    @classmethod
    def merge(self, plist, attributes=None, conflict=None):
        """returns a CurveAppearanceProperties object formed by merging a list
        of other CurveAppearanceProperties objects

        **Note:** This is a class method, so it can be called without previously
        instantiating an object

        :param plist: (sequence<CurveAppearanceProperties>) objects to be merged
        :param attributes: (sequence<str>) the name of the attributes to
                           consider for the merge. If None, all the attributes
                           will be merged
        :param conflict: (callable) a function that takes 2 objects (having a
                         different attribute)and returns a value that solves the
                         conflict. If None is given, any conflicting attribute
                         will be set to None.

        :return: (CurveAppearanceProperties) merged properties
        """

        n = len(plist)
        if n < 1: raise ValueError("plist must contain at least 1 member")
        plist = copy.deepcopy(plist)
        if n == 1: return plist[0]
        if attributes is None: attributes = ["sStyle", "sSize", "sColor", "sFill", "lStyle", "lWidth", "lColor",
                                             "cStyle", "cFill", "yAxis", "title"]
        if conflict is None: conflict = CurveAppearanceProperties.inConflict_none
        p = CurveAppearanceProperties()
        for a in attributes:
            alist = [p.__getattribute__(a) for p in plist]
            p.__setattr__(a, alist[0])
            for ai in alist[1:]:
                if alist[0] != ai:
                    # print "MERGING:",alist[0],ai,conflict(alist[0],ai)
                    p.__setattr__(a, conflict(alist[0], ai))
                    break
        return p

    def applyToCurve(self, curve):
        """applies the current properties to a given curve
        If a property is set to None, it is not applied to the curve"""
        raise DeprecationWarning(
            "CurveAppearanceProperties.applyToCurve() is deprecated. Use TaurusCurve.setAppearanceProperties() instead")
        curve.setAppearanceProperties(self)