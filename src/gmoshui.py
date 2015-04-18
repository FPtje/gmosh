#!/usr/bin/env python3
"""Starts the user interface of gmoshui."""

from view import mainwindow
from PySide import QtCore, QtGui
from functools import partial
import workshoputils
import sys

class ControlMainWindow(QtGui.QMainWindow):
    """Spawns the main window"""
    def __init__(self, parent = None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

def main():
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    connectMainWindowSignals(mySW.ui)
    mySW.show()
    sys.exit(app.exec_())

def errorMsg(s):
    msgBox = QtGui.QMessageBox()
    msgBox.setText(s)
    msgBox.exec_()

#######
# Workshop tools signals
#######

def wsIdInfo(widget):
    workshopid = widget.wsID.value()
    info = workshoputils.workshopinfo([workshopid])
    if not info:
        errorMsg("Unable to retrieve addon info. Make sure the workshop ID is correct.")
        return

    return info

def wsGetInfoClicked(widget):
    info = wsIdInfo(widget)
    if not info: return

    info = info[0]
    widget.wsName.setText(info['title'])
    widget.wsDescription.setText(info['description'])
    widget.wsAuthorSteam.setValue(float(info['creator']))
    widget.wsBanned.setCheckState(info['banned'] != 0 and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
    widget.wsBanReason.setText(info['ban_reason'])
    tags = ', '.join(list(filter(lambda x: x != "Addon", map(lambda x: x['tag'], info['tags']))))
    widget.wsTags.setText(tags)

    widget.wsViews.setValue(info['views'])
    widget.wsSubscriptions.setValue(info['subscriptions'])
    widget.wsFavorites.setValue(info['favorited'])

def wsDownloadClicked(widget):
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    workshoputils.download([widget.wsID.value()], selectedFiles[0], widget.wsExtract.isChecked())

def connectMainWindowSignals(widget):
    widget.wsGetInfo.clicked.connect(partial(wsGetInfoClicked, widget))
    widget.wsDownload.clicked.connect(partial(wsDownloadClicked, widget))

main();
