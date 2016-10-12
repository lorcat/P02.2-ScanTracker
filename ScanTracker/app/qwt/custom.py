__author__ = 'Konstantin Glazyrin'

from PyQt4 import QtGui, Qwt5, Qt, QtCore

from app.common.common import Checker
from app.config.graphics import DARKGRAY, RED, WHITE, BLACK

class Symbol(Qwt5.QwtSymbol, Checker):
    def __init__(self, style=None, sColor=None, sFill=None, sWidth=None, sSize=None):
        Checker.__init__(self)

        pen, brush = QtGui.QPen(), QtGui.QBrush()
        if self.check(sColor, QtGui.QColor):
            pen.setColor(sColor)
        else:
            pen.setColor(RED)

        if self.check(sWidth, int):
            pen.setWidth(sWidth)
        else:
            pen.setWidth(1)

        if self.check(sWidth, QtGui.QColor):
            brush.setColor(sFill)
        else:
            brush.setColor(RED)

        brush.setStyle(Qt.Qt.SolidPattern)

        if sSize is None or not isinstance(sSize, int):
            sSize = 10

        sSize = QtCore.QSize(sSize, sSize)

        try:
            Qwt5.QwtSymbol.__init__(self, style, brush, pen, sSize)
        except TypeError:
            Qwt5.QwtSymbol.__init__(self, Qwt5.QwtSymbol.Ellipse, brush, pen, sSize)

class CustomPointMarker(Qwt5.QwtPlotMarker, Checker):
    def __init__(self, symbol=None, cBorder=None, cWidth=None, cFill=None, cFont=None):
        Qwt5.QwtPlotMarker.__init__(self)
        Checker.__init__(self)

        if self.check(symbol, Symbol) or self.check(symbol, Qwt5.QwtSymbol):
            self.setSymbol(symbol)

        pen, brush = QtGui.QPen(), QtGui.QBrush()
        font = None

        if self.check(cBorder, QtGui.QColor):
            pen.setColor(cBorder)
        else:
            pen.setColor(BLACK)

        if self.check(cFill, QtGui.QColor):
            brush.setColor(cFill)
        else:
            brush.setColor(WHITE)

        label = self.label()
        label.setBackgroundPen(pen)
        label.setBackgroundBrush(brush)

        if self.check(cFont, QtGui.QFont):
            label.setFont(cFont)

        self.setLabel(label)


class VerticalMarker(Qwt5.QwtPlotMarker, Checker):
    def __init__(self, lColor=None, lWidth=None, lStyle=None):
        Checker.__init__(self)

        self.__style, self.__color, self.__lw = None, None, None

        pen = QtGui.QPen()
        if self.check(lColor, QtGui.QColor):
            self.__color = lColor
        else:
            self.__color = RED

        pen.setColor(self.__color)

        if self.check(lWidth, int):
            self.__lw = lWidth
        else:
            pen.setWidth(1)
            self.__lw = 1

        pen.setWidth(self.__lw)

        if self.check(lStyle):
            self.__style = lStyle
        else:
            self.__style = Qt.Qt.DashLine

        pen.setStyle(self.__style)

        Qwt5.QwtPlotMarker.__init__(self)

        self.setLineStyle(Qwt5.QwtPlotMarker.VLine)
        self.setXValue(0)
        self.setLinePen(pen)

    @property
    def style(self):
        return self.__style

    @property
    def lwidth(self):
        return self.__lw

    @property
    def color(self):
        return self.__color

class CustomGrid(Qwt5.QwtPlotGrid, Checker):
    def __init__(self, lColor=None, lWidth=None, cStyle=None):
        Checker.__init__(self)

        Qwt5.QwtPlotGrid.__init__(self)

        pen = QtGui.QPen()
        if self.check(lColor, QtGui.QColor):
            pen.setColor(lColor)
        else:
            pen.setColor(DARKGRAY)

        if self.check(lWidth, int):
            pen.setWidth(lWidth)
        else:
            pen.setWidth(1)

        if self.check(cStyle):
            pen.setStyle(cStyle)

        self.setPen(pen)