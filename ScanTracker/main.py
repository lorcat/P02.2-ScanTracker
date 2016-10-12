__author__ = 'Konstantin Glazyrin'

import os
import sys

from taurus.qt.qtgui.application import TaurusApplication
from app.ui.gui_window import MainWindow
from app.ui.gui_splash import SplashWindow


def main():
    sys.argv.append("--taurus-polling-period=100")
    app = TaurusApplication(sys.argv)
    app.processEvents()

    # file path with profiles
    config_path = os.path.join(os.path.dirname(__file__), 'app', 'config')

    # main window
    window = MainWindow(config_path=config_path)

    if window.config is not None:
        app.exec_()
    else:
        app.exit(-1)

if __name__ == "__main__":
    main()
