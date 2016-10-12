__author__ = 'Konstantin Glazyrin'

import numpy as np
from PyQt4 import QtGui, QtCore, Qt

from app.pymca.ScanWindow import ScanWindow
from app.common import logger
from app.ui.base_ui.ui_scanwindow import Ui_scanWindow

from app.ui.gui_widget_list import ListScansWidget, ListChannelWidget
from app.ui.gui_widget_channel import ChannelWidget
from app.storage.events import *

KEY_X, KEY_Y, KEY_NORM = "X", "Y", "NORM"

class CustomScanWindow(QtGui.QWidget, Ui_scanWindow, logger.LocalLogger):

    signrequestreplot = QtCore.pyqtSignal()

    def __init__(self, storage=None, name="", parent=None, debug_level=None):
        QtGui.QWidget.__init__(self, parent=parent)

        logger.LocalLogger.__init__(self, parent=parent, debug_level=debug_level)

        Ui_scanWindow.setupUi(self, self)

        self.__init_variables(storage=storage, name=name)
        self.__init_ui()
        self.__init_events()

    def __init_variables(self, storage=None, name=None):
        # external storage of scan data
        self.__storage = storage

        # pymca scan widget

        self.__scanwdgt = ScanWindow(self.widget_graph, name=name)

        # scan and channel lists
        self.__scanlist = ListScansWidget(parent=self, debug_level=self.debug_level)
        self.__channellist = ListChannelWidget(parent=self, debug_level=self.debug_level)

        # channel information
        self.__selchannels = {KEY_X: None, KEY_Y: None, KEY_NORM: None}

        # container with channel widget list
        self.__chselwdgts = []

    def __init_ui(self):
        layout = self.page_scans.layout()
        layout.addWidget(self.__scanlist, layout.rowCount()+1, layout.columnCount()-1)

        self.widget_graph.layout().addWidget(self.__scanwdgt)
        self.page_channels.layout().addWidget(self.__channellist)

        self.splitter.setStretchFactor(0, 25)
        self.splitter.setStretchFactor(1, 5)

    def __init_events(self):
        self.connect(self.__storage, QtCore.SIGNAL(EVENT_SCAN_STARTED), self.actionScanStarted)
        self.connect(self.__storage, QtCore.SIGNAL(EVENT_SCAN_CHANGED), self.actionScanChanged)
        self.connect(self.__storage, QtCore.SIGNAL(EVENT_SCAN_FINISHED), self.actionScanFinished)

        self.connect(self.__scanlist, QtCore.SIGNAL("itemSelectionChanged()"), self.actionSelectScan)

        self.registerReplotSignal(self.replot)

    def actionApplyDerivative(self):
        if self.areChannelsPrepared():
            self.requestReplot()

    def actionApplyInversion(self):
        if self.areChannelsPrepared():
            self.requestReplot()

    def actionScanChanged(self, scan):
        if self.areChannelsPrepared() and self.isFastReplotNeeded():
            self.requestReplot()

    def actionScanStarted(self, scan):
        # do not change selection, update list view
        wlist = []
        for s in self.__storage.storage:
            str = "%i: %s" % (s.serial, s.cmd)
            motors = ";".join(s.getMotorLabels())
            tooltip = "Scan #%i; Motors (%s); Macro: %s;" % (s.serial, motors, s.cmd)
            templ = QtGui.QListWidgetItem(str)
            templ.setToolTip(tooltip)
            wlist.append(templ)

        self.__scanlist.clear()

        for w in wlist:
            self.__scanlist.addItem(w)

        self.cb_latest.setChecked(True)
        if self.isTrackingLatest():
            self.__scanwdgt.clear()
            self.__scanlist.setCurrentItem(wlist[-1])

            if self.areChannelsPrepared():
                self.requestReplot()

    def actionScanFinished(self, scan):
        pass

    def areChannelsPrepared(self):
        """
        Function checking and reporting if proper channel are selected for plotting
        :return:
        """
        # test based on selected self.__chselwdgts
        labelx, labely, labelnorm = None, None, None
        for w in self.__chselwdgts:
            if isinstance(w, ChannelWidget) and w.isX():
                labelx = str(w.label).lower()
            if isinstance(w, ChannelWidget) and w.isY():
                labely = str(w.label).lower()
            if isinstance(w, ChannelWidget) and w.isNorm():
                labelnorm = str(w.label).lower()

        res, count = True, 0
        if labelx is not None:
            self.__selchannels[KEY_X] = labelx
            count += 1
        else:
            self.__selchannels[KEY_X] = None

        if labely is not None:
            self.__selchannels[KEY_Y] = labely
            count += 1
        else:
            self.__selchannels[KEY_Y] = None

        if labelnorm is not None:
            self.__selchannels[KEY_NORM] = labelnorm
        else:
            self.__selchannels[KEY_NORM] = None

        if count != 2:
            res = False
            self.error("Not enough channels selected for a plot")

        return res

    def isTrackingLatest(self):
        """
        Function reporting if we want to always track the last scan
        :return:
        """
        return self.cb_latest.isChecked()

    def actionSelectScan(self):
        """
        Function happening upon a scan selection
        :param index:
        :return:
        """
        self._buildChannelList()

        # if Y and X signals are set - replot
        if self.areChannelsPrepared():
            self.info("Requesting replot from %s.actionSelectScan" % self.classname())
            self.requestReplot()
        else:
            self.info("Channels are not prepared %s " % self.__selchannels)

    def _buildChannelList(self):
        """
        Builds a list of channel selectors - X, Y, Normalization
        :return:
        """
        # get selected channels, check that all of them have the same channel set - motor+counters
        indexes = [i.row() for i in list(self.__scanlist.selectedIndexes())]

        self.info("Selection indexes list %s" % indexes)

        if len(indexes)==0:
            return

        bfailed = False
        ref_counters = None
        for i in indexes:

            if i == 0:
                ref_counters = self.__storage.getScan(i).getLabels().sort()
                continue

            counters = self.__storage.getScan(i).getLabels().sort()
            if counters != ref_counters:
                bfailed = True
                self.error("Scans are different by nature")
                break

        if not bfailed:
            scan = self.__storage.getScan(indexes[0])
            # motors are first
            motors = [label.lower() for label in scan.getMotorLabels()]
            counters = [label.lower() for label in scan.getCounterLabels()]

            labels = motors+counters

            self.info("Creating channel list %s" % labels)

            btrack = True
            if self.isTrackingLatest() and self.__selchannels[KEY_Y] is not None or self.__selchannels[KEY_X] is not None:
                bfirst = False

            # clear previous widgets
            self._clearChSelWdgts()

            # clear first motor
            for (i, l) in enumerate(labels):
                l = str(l).lower()

                w = ChannelWidget()
                w.setLabel(l)

                # select first channel and tracking is set
                if i==0 and self.isTrackingLatest() and self.__selchannels[KEY_X] not in labels:
                    w.actionSetX(True, breport=False)
                elif self.__selchannels[KEY_X]==l:
                    # select channels if they have been selected earlier
                    w.actionSetX(True, breport=False)

                # if there is no y axis but tracking is set - set first channel as the channel of interest
                if i == len(motors) and self.isTrackingLatest() and self.__selchannels[KEY_Y] not in labels:
                    w.actionSetY(True, breport=False)
                elif self.__selchannels[KEY_Y]==l:
                    w.actionSetY(True, breport=False)

                if self.__selchannels[KEY_NORM]==l:
                    w.actionSetNorm(True, breport=False)

                # save them into an internal storage
                self.__chselwdgts.append(w)
                # register their events
                self._registerChSelWdgtsEvents(w)

                # make sure we have same size as widget
                templ = QtGui.QListWidgetItem()
                templ.setSizeHint(w.sizeHint())

                # finally add widgets to the list
                self.__channellist.addItem(templ)
                self.__channellist.setItemWidget(templ, w)

    def requestReplot(self):
        """
        Emits a signal requesting a replot of graphs
        :return:
        """
        self.signrequestreplot.emit()

    def registerReplotSignal(self, func):
        """
        Register a function processed upon a replot request signal
        :param func:
        :return:
        """
        self.signrequestreplot.connect(func)

    def _clearChSelWdgts(self):
        """
        Clears channel widgets responsible for
        :return:
        """
        for w in self.__chselwdgts:
            if w is not None and isinstance(w, ChannelWidget):
                w.deleteLater()

        self.__channellist.clear()
        self.__chselwdgts = []

    def _registerChSelWdgtsEvents(self, widget):
        if widget is not None and isinstance(widget, ChannelWidget):
            widget.registerXChange(self.actionChSelX)
            widget.registerYChange(self.actionChSelY)
            widget.registerNormChange(self.actionChSelNorm)

    def actionChSelX(self, bflag, widget):
        """
        Function taking care for single x channel selection
        :param bflag: bool() - change signal from widget
        :param widget: ChannelWidget()
        :return:
        """
        if bflag == False:
            return

        # we process only selected flag
        for w in self.__chselwdgts:
            if isinstance(w, ChannelWidget):
                bselected = False
                if w == widget:
                    bselected = True
                w.actionSetX(bselected, breport=False)

        if self.areChannelsPrepared():
            self.info("Requesting replot from %s.actionChSelX" % self.classname())
            self.requestReplot()

    def actionChSelY(self, bflag, widget):
        """
        Function taking care for single y channel selection
        :param bflag: bool() - change signal from widget
        :param widget: ChannelWidget()
        :return:
        """
        if bflag == False:
            return

        # we process only selected flag
        for w in self.__chselwdgts:
            if isinstance(w, ChannelWidget):
                bselected = False
                if w==widget:
                    bselected = True
                w.actionSetY(bselected, breport=False)

        if self.areChannelsPrepared():
            self.info("Requesting replot from %s.actionChSelY" % self.classname())
            self.requestReplot()

    def actionChSelNorm(self, bflag, widget):
        """
        Function taking care for single normalization channel selection
        :param bflag: bool() - change signal from widget
        :param widget: ChannelWidget()
        :return:
        """

        # we process only selected flag
        if bflag != False:
            for w in self.__chselwdgts:
                if isinstance(w, ChannelWidget):
                    bselected = False
                    if w == widget:
                        bselected = True
                    w.actionSetNorm(bselected, breport=False)

        if self.areChannelsPrepared():
            self.info("Requesting replot from %s.actionChSelNorm" % self.classname())
            self.requestReplot()

    def isFastReplotNeeded(self):
        res = True
        # get current selection by indexes
        selection = [int(index.row()) for index in list(self.__scanlist.selectedIndexes())]

        # do nothing unless there is a last item selection
        if not self.__scanlist.count()-1 in selection:
            res = False

        return res


    def replot(self):
        """
        Function taking care for replotting on appropritate signal - channels checked, scans selected
        :return:
        """
        self.__scanwdgt.clear()

        # get current selection by indexes
        selection = [int(index.row()) for index in list(self.__scanlist.selectedIndexes())]

        self.info("Plotting selection %s" % selection)


        for index in selection:
            berror = False
            scan = self.__storage.getScan(index)

            legend = "Scan %i" % (scan.serial)

            x, y = scan.getChannelByLabel(self.__selchannels[KEY_X]), scan.getChannelByLabel(self.__selchannels[KEY_Y])
            norm = scan.getChannelByLabel(self.__selchannels[KEY_NORM])

            if x is not None and y is not None:
                xp, yp = np.array(x.points), np.array(y.points)

                # normalization occures without a derivative
                if norm is not None and not self.isDerivativeApplied():
                    normp = np.array(norm.points)

                    # perform a normalization
                    for (i, ty) in enumerate(yp):
                        try:
                            temp = ty/normp[i]
                        except ZeroDivisionError:
                            temp = 0
                            self.error("Normalization (%s) point with index (%i) raises a ZeroDivisionError" % (norm.label, i))

                        yp[i] = temp
                elif self.isDerivativeApplied() and len(xp) > 1:
                    # calculate both part of derivative
                    cx, cy = np.diff(np.array([xp, yp]))

                    # test for 0 in the signal
                    if 0. not in cx:
                        yp = cy/cx
                        xp = np.resize(xp, [len(xp)-1])
                    else:
                        self.error("Error with scan")
                        berror = True

                # make data inversion if requested
                if self.isInversionApplied() and len(xp) > 0:
                    yp = -yp

                # draw a plot unless an error has occured
                if not berror:
                    self.__scanwdgt.newCurve(xp, yp, legend=legend, xlabel=x.label, ylabel=y.label, replace=False)

    def isDerivativeApplied(self):
        """
        Performes a test if user has requested a derivative calculation
        :return: bool()
        """
        return self.cb_derivative.isChecked()

    def isInversionApplied(self):
        """
        Performes a test if user has requested a data inversion
        :return: bool()
        """
        return self.cb_invert.isChecked()