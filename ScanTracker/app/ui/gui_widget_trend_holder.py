__author__ = 'p02user'

import copy

from PyQt4 import Qt, QtGui, QtCore
from PyQt4.Qwt5.Qwt import QwtPlot, QwtSymbol, QwtPlotMarker, QwtPlotGrid

from app.common import logger
from app.ui.base_ui.ui_trend_holder import Ui_trend_holder
from app.taurus.custom import CustomTaurusTrend, KEYTT_CEN, KEYTT_FWHM, KEYTT_CENMASS
from app.storage.main import Scan

from app.taurus.custom import CurveAppearanceProperties
from app.qwt.custom import VerticalMarker, CustomPointMarker, CustomGrid
from app.common.common import Checker


class WidgetTrendHolder(QtGui.QWidget, Ui_trend_holder, logger.LocalLogger, Checker):
    DEFAULT_COLUMN_NUMBER = 2
    DEFAULT_CURVE_NAME = 'data'

    def __init__(self, parent=None, debug_level=None):

        QtGui.QWidget.__init__(self, parent=parent)
        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)
        Checker.__init__(self)

        Ui_trend_holder.setupUi(self, self)

        self.__init_variables()
        self.__init_ui()
        self.__init_events()

    def __init_variables(self):
        # storage for TaurusTrend objects
        self.__trends = []

        # xlabel - reference for label name
        self.__xlabel = ''

        # reference for a scan object
        self.__scan = None
        self.__bstarted = False
        self._cleanScan()

        # column range
        self.__max_col = self.DEFAULT_COLUMN_NUMBER

        # curve config
        self.__curve_config = CurveAppearanceProperties(sStyle=QwtSymbol.Ellipse, sSize=10, sColor=QtGui.QColor('red'),
                                                        sFill=True,
                                                        lStyle=None, lWidth=2, lColor='blue', cStyle=None,
                                                        yAxis=None, cFill=None, title=None, visible=None)


        # config for position marker
        self.__posmarker_config = None
        self.__pointmarker_config = None
        self.__motormarker_config = None

        # variable holding motors used for timescan
        self.__tsmotors = None
        self.__tspointnumber = 500

        # config for general view of the plot
        self.__background_config = None
        self.__axisfont_config = None
        self.__axislabelfont_config = None
        self.__grid_config = None

    def __init_ui(self):
        pass

    def __init_events(self):
        pass

    @property
    def trends(self):
        return self.__trends

    @property
    def xlabel(self):
        return self.__xlabel

    @xlabel.setter
    def xlabel(self, value):
        self.setXLabel(value)

    @property
    def columns(self):
        return self.__max_col

    @columns.setter
    def columns(self, value):
        self.setNumberColumns(value)

    def setPositionMarkerConfig(self, config):
        """
        Sets configuration regarding position marker
        :param config: QwtPlotMarker() or VerticalMarker()
        :return:
        """
        if self.check(config, QwtPlotMarker) or self.check(config, VerticalMarker):
            self.__posmarker_config = config

            for tt in self.trends:
                tt.setPositionMarker(self.__posmarker_config)
        else:
            self.error('Wrong position marker config (%s)' % config)

    def setMotorMarkerConfig(self, config):
        """
        Sets configuration regarding position marker
        :param config: QwtPlotMarker() or VerticalMarker()
        :return:
        """
        if self.check(config, QwtPlotMarker) or self.check(config, VerticalMarker):
            self.__motormarker_config = config

            for tt in self.trends:
                tt.setMotorMarker(self.__motormarker_config)
        else:
            self.error('Wrong position marker config (%s)' % config)

    def setPointMarkerConfig(self, config):
        """
        Sets configuration regarding point marker
        :param config: QwtPlotMarker()
        :return:
        """
        if self.check(config, QwtPlotMarker) or self.check(config, CustomPointMarker):
            self.__pointmarker_config = config

            for tt in self.trends:
                tt.setPositionMarker(self.__pointmarker_config)
        else:
            self.error('Wrong point marker config (%s)' % config)

    def setTimescanMotors(self, config):
        """
        Sets configuration regarding motors which considered as timescan motors by default
        :param config: list() or tuple()
        :return:
        """
        if self.check(config, list) or self.check(config, tuple):
            self.__tsmotors = config
        else:
            self.error('Wrong timescan motors config (%s)' % config)

    def setTimescanPointNumber(self, config):
        """
        Sets configuration regarding motors which considered as timescan motors by default
        :param config: list() or tuple()
        :return:
        """
        if self.check(config, int):
            self.__tspointnumber = config
        else:
            self.error('Wrong timescan point limit number config (%s)' % config)

    def setAxisFontConfig(self, config):
        """
        Sets configuration axis font config
        :param config: QFont()
        :return:
        """
        if self.check(config, QtGui.QFont):
            self.__axisfont_config = config

            for tt in self.trends:
                self._adjustFont(tt, config)
        else:
            self.error('Wrong axis font config (%s)' % config)

    def setAxisLabelFontConfig(self, config):
        """
        Sets configuration axis label font config
        :param config: QFont()
        :return:
        """
        if self.check(config, QtGui.QFont):
            self.__axislabelfont_config = config

            for tt in self.trends:
                self._adjustAxisLabelFont(tt, config)
        else:
            self.error('Wrong axis font config (%s)' % config)

    def setGridConfig(self, config):
        """
        Sets configuration axis font config
        :param config: QwtPlotGrid() or CustomGrid()
        :return:
        """
        if self.check(config, QwtPlotGrid) or self.check(config, CustomGrid):
            self.__grid_config = config

            for tt in self.trends:
                self._adjustGrid(tt, config)
        else:
            self.error('Wrong plot grid config (%s)' % config)

    def setBackgroundConfig(self, config):
        """
        Sets configuration axis font config
        :param config: QwtPlotGrid() or
        :return:
        """
        if self.check(config, QtGui.QColor):
            self.__background_config = config

            for tt in self.trends:
                self._adjustBackground(tt, config)
        else:
            self.error('Wrong plot background color config (%s)' % config)

    def setXLabel(self, value):
        """
        Sets xlabel of the TaurusTrend plots
        :param value: str()
        :return:
        """
        if self.check(value, str) or self.check(value, unicode):
            self.__xlabel = value

    def setNumberColumns(self, value):
        """
        Sets maximum number of columns for visualization
        :param value: int() - maximum number of columns
        :return:
        """
        try:
            value = int(value)
        except ValueError:
            value = self.DEFAULT_COLUMN_NUMBER

        if value is not None and isinstance(value, int):
            self.__max_col = value

            self.setLoadingPage()
            self.reorganize()
            self.setPlotPage()

    def setCurveConfig(self, config):
        if config is not None and isinstance(config, CurveAppearanceProperties):
            self.__curve_config = config

    def setScan(self, scan):
        """
        Sets a new scan - reference, events, etc.
        :param scan: Scan() object
        :return:
        """
        if self.check(scan, Scan):
            self._cleanScan()

            self.__scan = scan
            self.__scan.registerStartEvent(self.processScanStart)
            self.__scan.registerChangeEvent(self.processScanChange)
            self.__scan.registerFinishEvent(self.processScanFinish)

    def _adjustGrid(self, wdgt, config):
        if self.check(wdgt, CustomTaurusTrend):
            grid = QwtPlotGrid()
            grid.setPen(config.majPen())

            wdgt._grid.detach()
            wdgt._grid = grid
            wdgt._grid.attach(wdgt)

    def _adjustFont(self, wdgt, config):
        if self.check(wdgt, CustomTaurusTrend):
            wdgt.setAxisFont(QwtPlot.xBottom, config)
            wdgt.setAxisFont(QwtPlot.yLeft, config)

    def _adjustAxisLabelFont(self, wdgt, config):
        if self.check(wdgt, CustomTaurusTrend):
            for axis in (QwtPlot.xBottom, QwtPlot.yLeft):
                label = wdgt.axisTitle(axis)
                label.setFont(config)
                wdgt.setAxisTitle(axis, label)

    def _adjustBackground(self, wdgt, config):
        # brush = QtGui.QBrush()
        # brush.setStyle(Qt.Qt.SolidPattern)
        # brush.setColor(config)
        if self.check(wdgt, CustomTaurusTrend):
            wdgt.setCanvasBackground(config)

    def _cleanScan(self):
        """
        Cleaning up previous scan information
        :return:
        """
        if self.check(self.__scan, Scan):
            self.__scan.uregisterStartEvent(self.processScanStart)
            self.__scan.unregisterChangeEvent(self.processScanChange)
            self.__scan.unregisterFinishEvent(self.processScanFinish)
        self.__scan = None
        self.__bstarted = False

        self.stack.setCurrentWidget(self.page_plots)

    def setVisibleWidget(self, index):
        """
        Changes appearance showing only a single widget selected by index
        :param index: int()
        :return:
        """
        if self.check(index, int) and 0 <= index < len(self.trends):
            for (i, tt) in enumerate(self.trends):
                bflag = False
                if i == index:
                    bflag = True
                    tt.setTitle('%s - %i/%i' % (tt.axisTitle(QwtPlot.yLeft).text(), index+1, len(self.trends)))
                tt.setEnabled(bflag)

            self.setLoadingPage()
            self.reorganize()
            self.setPlotPage()

    def getVisibleWidgetIndex(self):
        """
        Returns information on index of visible widget, if more than one widget is visible - return None
        :return: int() or None
        """
        count = 0
        index = None
        for (i, tt) in enumerate(self.trends):
            if tt.isEnabled():
                count += 1
                index = i

        if count > 1:
            index = None
        return index

    def proccessManualCalculation(self, wdgt):
        """
        Processes a manual calculation, make gui show the data
        :param wdgt:
        :return:
        """
        value = wdgt._getStatistics(KEYTT_FWHM)
        if self.check(value, float):
            self.stat_fwhm.setText('%6.4f' % value)

        value = wdgt._getStatistics(KEYTT_CEN)
        if self.check(value, QtCore.QPointF):
            self.stat_center.setText('%6.4f' % value.x())

        value = wdgt._getStatistics(KEYTT_CENMASS)
        if self.check(value, QtCore.QPointF):
            self.stat_cms.setText('%6.4f' % value.x())


    def allocate(self, number):
        """
        Allocates proper number of TaurusTrend panels
        :param number: int()
        :return:
        """
        bmodified = True
        if number > len(self.trends):
            for i in range(number - len(self.trends)):
                tt = CustomTaurusTrend(parent=self, debug_level=self.debug_level)
                tt.setXIsTime(False)
                tt.setEnabled(True)
                self._setDefaultPlotNaming(tt)

                # signal for reporting calculated data - manually calculated
                tt.registerStatCalculated(self.proccessManualCalculation)

                if self.check(self.__pointmarker_config):
                    tt.setPointMarker(self.__pointmarker_config)

                if self.check(self.__posmarker_config):
                    tt.setPositionMarker(self.__posmarker_config)

                if self.check(self.__motormarker_config):
                    tt.setMotorMarker(self.__motormarker_config)

                if self.check(self.__background_config):
                    self._adjustBackground(tt, self.__background_config)

                if self.check(self.__axisfont_config):
                    self._adjustFont(tt, self.__axisfont_config)

                if self.check(self.__grid_config):
                    self._adjustGrid(tt, self.__grid_config)

                if self.check(self.__axislabelfont_config):
                    self._adjustAxisLabelFont(tt, self.__axislabelfont_config)

                self.trends.append(tt)
        elif number < len(self.trends):
            # cleaning up objects which are not needed for scan representation
            for i in range(len(self.trends) - number):
                tt = self.trends.pop(-1)
                tt.setParent(None)
                tt.hide()
                tt.deleteLater()
        else:
            # no change in number
            bmodified = False

        if bmodified:
            self.reorganize()

    def reorganize(self):
        """
        Reorganizes widgets on a layout
        :return:
        """

        layout = self.plots.layout()
        for wdgt in self.plots.children():
            if self.check(wdgt, CustomTaurusTrend):
                layout.removeWidget(wdgt)
                wdgt.setParent(None)

        row, col = 0, 0
        for (i, tt) in enumerate(self.trends):
            if tt.isEnabled():
                if col == self.__max_col:
                    row, col = row + 1, 0

                layout.addWidget(tt, row, col)
                col += 1

    def setLoadingPage(self):
        """
        Sets loading page of self.stack as a visible one
        :return:
        """
        self.stack.setCurrentWidget(self.page_loading)

    def setPlotPage(self):
        """
        Sets the plot page of self.stack as visible one
        :return:
        """
        self.stack.setCurrentWidget(self.page_plots)

    def processScanChange(self):
        """
        Processes new scan, gets points plots them
        :return:
        """
        scan = self.__scan

        if self.check(scan, Scan):
            motors = scan.getMotorLabels()

            if self.__xlabel not in motors and len(motors):
                self.__xlabel = motors[0]
            elif len(motors) == 0:
                self._cleanScan()

            btsmode = False
            if self.__xlabel == motors[-1]:
                btsmode = True

            if self.__scan is not None:
                x = self.preparePoints(btsmode, scan.getChannelByLabel(self.__xlabel).points)

                # set data from the scan for the
                for tt in self.trends:
                    cname = tt.getCurveNames()[0]
                    curve = tt.getCurve(cname)

                    y = self.preparePoints(btsmode, scan.getChannelByLabel(cname).points)

                    curve.setData(x, y)

                    tt.calculatePlotStatistics()

                    tt.autoScaleAllAxes()
                    tt.doReplot()

    def preparePoints(self, btsmode, data):
        """
        Prepares a point array based on information about timescan mode
        :param btsmode: bool()
        :param data: list()
        :return: list()
        """
        res = data
        numpoints = self.__tspointnumber
        if btsmode and self.check(numpoints, int):
            res = data[-numpoints:]
        return res


    def processScanFinish(self):
        pass

    def processScanStart(self):
        """
        Processes scan data, gets channels, allocates necessary number of channels
        :return:
        """
        scan = self.__scan
        self.setLoadingPage()

        self._resetGUIStatistics()

        if self.check(scan, Scan):
            counters = scan.getCounterLabels()
            motors = scan.getMotorLabels()

            # reset timescan mode every time to be sure
            if self.__xlabel == motors[-1]:
                self.__xlabel = None

            if self.__xlabel not in motors and len(motors):
                self.__xlabel = motors[0]
            elif len(motors) == 0:
                self._cleanScan()

            # check if any of the motors is in the timescan mode range
            btsfound = False
            if self.__tsmotors:
                for tsmotor in self.__tsmotors:
                    tsmotor = str(tsmotor)
                    for motor in motors:
                        motor = str(motor)
                        if tsmotor in motor:
                            btsfound = True

                            # timestamp looks like a last motor
                            self.__xlabel = str(motors[-1])
                            break
                    if btsfound:
                        break

            if self.__scan is not None:
                ch_number = len(counters)
                if ch_number > 0:
                    self.allocate(ch_number)

                    # let the TaurusTrend objects be aware of the timescan mode
                    for tt in self.trends:
                        tt.setTimescanMode(btsfound)

                # set the information on axis, other things
                for (i, cnt) in enumerate(counters):
                    self.setPlotWidgetInfo(self.trends[i], title='', xlabel=self.__xlabel, ylabel=cnt)

        self.setPlotPage()

    def setPlotWidgetInfo(self, wdgt, title='', xlabel='x', ylabel='y'):
        """
        Sets up a curve for a specific widget
        :param wdgt: TaurusTrend()
        :param title: str()
        :param xlabel: str()
        :param ylabel: str()
        :return:
        """
        title, xlabel, ylabel = title or '', xlabel or 'x', ylabel or 'y'

        # check if such curvename exists
        curve_names = wdgt.getCurveNames()

        wdgt.setTitle(str(title))
        wdgt.setAxisTitle(QwtPlot.xBottom, xlabel)

        if ylabel in curve_names:
            curve = wdgt.getCurve(ylabel)
            curve.setData([], [])
        else:

            wdgt.setAxisTitle(QwtPlot.yLeft, ylabel)
            wdgt.clearAllRawData()

            wdgt.attachRawData({'x': [], 'y': [], 'title': ylabel})

            if self.__curve_config is not None:
                curve = wdgt.getCurve(ylabel)

                self.setAppearanceProperties(curve, self.__curve_config)

    def _setDefaultPlotNaming(self, wdgt):
        if self.check(wdgt, CustomTaurusTrend):
            wdgt.setAxisTitle(QwtPlot.xBottom, '<mov>')
            wdgt.setAxisTitle(QwtPlot.yLeft, '<counter>')


    def makeAllVisible(self):
        """
        Make all widgets visible
        :return:
        """
        for tt in self.trends:
            tt.setEnabled(True)
            tt.setTitle('')
        self.reorganize()

    def isTimescanMode(self):
        """
        Test for a timescan mode of the current scan
        :return: bool()
        """
        res = False
        scan = self.__scan
        if self.__tsmotors is not None and self.check(scan, Scan):
            for tsmotor in self.__tsmotors:
                for motor in scan.getMotorLabels():
                    if tsmotor in motor:
                        res = True
                        break
                if res:
                    break
        return res

    def processExternalPosition(self, name, position):
        """
        Receives information on the external position and plots it
        :param name: str() - motor name
        :param position: float()
        :return:
        """

        for tt in self.trends:
            tt.setMotorMarkerPosition(position)

    def _resetGUIStatistics(self):
        """
        Resets fields with statistics
        :return:
        """
        for wdgt in (self.stat_center, self.stat_fwhm, self.stat_cms):
            wdgt.setText('')

    def setAppearanceProperties(self, curve, prop):
        """
        Corrected from Taurus - Applies the given CurveAppearanceProperties object (prop) to the curve.
        If a given property is set to None, it is not applied

        :param prop: (CurveAppearanceProperties)
        """
        prop = copy.deepcopy(prop)

        s = QwtSymbol(curve.symbol())

        spen, sbrush = QtGui.QPen(), QtGui.QBrush()

        if prop.sStyle is not None: s.setStyle(QwtSymbol.Style(prop.sStyle))
        if prop.sSize is not None: s.setSize(prop.sSize)
        if prop.sWidth is not None: spen.setWidth(prop.sWidth)
        if prop.sColor is not None:
            spen.setColor(Qt.QColor(prop.sColor))
        if prop.sFill is not None:
            if prop.sFill:
                sbrush.setColor(Qt.QColor(prop.sFill))
                sbrush.setStyle(Qt.Qt.SolidPattern)
            else:
                sbrush.setStyle(Qt.Qt.NoBrush)

        s.setPen(spen)
        s.setBrush(sbrush)

        lpen, lbrush = QtGui.QPen(), QtGui.QBrush()
        if prop.lStyle is not None:
            lpen.setStyle(prop.lStyle)
        if prop.lWidth is not None:
            lpen.setWidth(prop.lWidth)
        if prop.lColor is not None:
            lpen.setColor(Qt.QColor(prop.lColor))
        if prop.cStyle is not None:
            curve.setStyle(prop.cStyle)
        if prop.cFill is not None:
            if prop.cFill:  # The area under the curve is filled with the same color as the curve but with 50% transparency
                color = lpen.color()
                color.setAlphaF(0.5)
                lbrush.setColor(color)
                lbrush.setStyle(Qt.Qt.SolidPattern)
            else:
                lbrush.setStyle(Qt.Qt.NoBrush)
        if prop.yAxis is not None:
            curve.setYAxis(prop.yAxis)
        if getattr(prop, "visible", None) is not None:
            curve.setVisible(prop.visible)

        curve.setBrush(lbrush)
        curve.setSymbol(s)
        curve.setPen(lpen)