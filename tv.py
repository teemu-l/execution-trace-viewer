import sys
from PyQt5 import QtWidgets
import qdarkstyle

from core import prefs
from gui.mainwindow import MainWindow

if __name__ == "__main__":
    APP = QtWidgets.QApplication(sys.argv)
    if prefs.USE_DARK_THEME:
        APP.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    else:
        APP.setStyle(prefs.LIGHT_THEME)
    WINDOW = MainWindow()
    WINDOW.show()
    sys.exit(APP.exec_())
