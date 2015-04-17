#!/usr/bin/env python3
"""Starts the user interface of gmoshui."""

from view import mainwindow
from PySide import QtCore, QtGui
import sys

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

def main():
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())

main();
