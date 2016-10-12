__author__ = 'Konstantin Glazyrin'

# python classes
from app.config.classes import *

# config dictionary keys
from app.config.keys import *

# markers for selected points
POINTMARKER = CustomPointMarker(symbol=Symbol(Ellipse, sColor=BLACK, sFill=WHITE, sWidth=2, sSize=15),
                                cBorder=WHITE, cFill=WHITE, cWidth=3)
# marker for selected position
POSITIONMARKER = VerticalMarker(lColor=RED, lWidth=2)

# marker for position tracking
MOTORMARKER = VerticalMarker(lColor=CYAN, lWidth=2, lStyle=Qt.Qt.SolidLine)

# grid for TT plots
TTGRID = CustomGrid(lColor=LIGHTGRAY, lWidth=1, cStyle=LINE_DASH)


# main startup variable
STARTUP = {
    # name distinguishing profile on loading
    KEYPROFILE_NAME: 'P02.2 profile (3 doors)',

    # Doors settings - should be valid doors
    KEYPROFILE_DOORS: ['haspp02ch2:10000/p02/door/haspp02ch2.01', 'haspp02ch2:10000/p02/door/haspp02ch2.02',
                       'haspp02ch2:10000/p02/door/haspp02ch2.03'],

    # view with plots
    KEYPROFILE_COLNUMBER: 2,


    # Plot specific parameters
    # curve settings
    KEYPROFILE_CURVE: CurveAppearanceProperties(sStyle=Ellipse, sSize=10, sWidth=3, sColor=DARKRED, sFill=RED,
                 lStyle=None, lWidth=2, lColor = RED, cStyle=None,
                 yAxis=None, cFill=None, title=None),

    # markers
    KEYPROFILE_POINTMARKER: POINTMARKER,
    KEYPROFILE_POSITIONMARKER: POSITIONMARKER,
    KEYPROFILE_MOTORMARKER: MOTORMARKER,

    # timescan motors - used to switch on or off the timescan mode
    KEYPROFILE_TIMESCAN: ['exp_dmy01'],

    # maximum number of points displayed for the timescan, int()
    KEYPROFILE_TIMESCANPOINTS: 100,

    # general plot parameters
    KEYPROFILE_TTAXISFONT: QtGui.QFont('Arial', 8, FONT_BOLD),
    KEYPROFILE_TTAXISLABELFONT: QtGui.QFont('Arial', 12, FONT_BOLD),
    KEYPROFILE_TTBACKGROUND: WHITE,
    KEYPROFILE_TTGRID: TTGRID,

    # Motor Format representation
    KEYPROFILE_MOTORFORMAT: '%6.4f',
}