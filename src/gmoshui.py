#!/usr/bin/env python3
"""Starts the user interface of gmoshui."""

from view import mainwindow, progressdialog
from PySide import QtCore, QtGui
from functools import partial
import workshoputils
import sys
import shiboken
from datetime import datetime

class ControlMainWindow(QtGui.QMainWindow):
    """Spawns the main window"""
    def __init__(self, parent = None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

def main():
    """Main method"""
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    connectMainWindowSignals(mySW.ui)
    mySW.show()
    sys.exit(app.exec_())

def errorMsg(s):
    """Show an error message box"""
    msgBox = QtGui.QMessageBox()
    msgBox.setText(s)
    msgBox.exec_()

class OutLog:
    def __init__(self, signal, out=None):
        """
        """
        self.signal = signal
        self.out = out

    def write(self, m):
        self.signal.emit(m)

        if self.out:
            self.out.write(m)

    def flush(x): pass

# Run something in the background
class WorkBackground(QtCore.QThread):
    target = id
    signal = QtCore.Signal(str)
    finished = QtCore.Signal()
    def run(self):
        oldstdout = sys.stdout
        sys.stdout = OutLog(self.signal, sys.stdout)

        self.target()
        self.signal.emit("FINISHED")

        sys.stdout = oldstdout
        self.finished.emit()

# Create progress dialog
def createProgressDialog(work):
    dialog = QtGui.QDialog()
    ui = progressdialog.Ui_Dialog()
    ui.setupUi(dialog)

    def onThreadOutput(text):
        if not shiboken.isValid(ui) or not shiboken.isValid(ui.progressText): return

        ui.progressText.moveCursor(QtGui.QTextCursor.End)
        if text[0] == "\r":
            #cursor = QtGui.QTextCursor(ui.progressText.textCursor())
            ui.progressText.moveCursor(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            ui.progressText.moveCursor(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)

        ui.progressText.insertPlainText(text)

    def enableButtons():
        ui.buttonBox.setEnabled(True)

    thread = WorkBackground()
    thread.target = work
    thread.signal.connect(onThreadOutput)
    thread.finished.connect(enableButtons)
    thread.start()

    dialog.show()
    dialog.exec_()
    thread.exit()


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


    created = QtCore.QDateTime.fromTime_t(info['time_created'])
    updated = QtCore.QDateTime.fromTime_t(info['time_updated'])
    widget.wsTimeCreated.setDateTime(created)
    widget.wsTimeUpdated.setDateTime(updated)

    widget.wsViews.setValue(info['views'])
    widget.wsSubscriptions.setValue(info['subscriptions'])
    widget.wsFavorites.setValue(info['favorited'])

def wsDownloadClicked(widget):
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    workshopid = widget.wsID.value()
    extract = widget.wsExtract.isChecked()
    def work():
        workshoputils.download([workshopid], selectedFiles[0], extract)

    createProgressDialog(work)


def connectMainWindowSignals(widget):
    widget.wsGetInfo.clicked.connect(partial(wsGetInfoClicked, widget))
    widget.wsDownload.clicked.connect(partial(wsDownloadClicked, widget))

try:
    main();
except KeyboardInterrupt: pass
