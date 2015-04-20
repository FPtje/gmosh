#!/usr/bin/env python3
"""Starts the user interface of gmoshui."""

from view import mainwindow, progressdialog
from PySide import QtCore, QtGui
from functools import partial
import workshoputils
import addoninfo
import gmafile
import sys
import shiboken
from datetime import datetime
import os
import re

class ControlMainWindow(QtGui.QMainWindow):
    """Spawns the main window"""
    def __init__(self, parent = None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Create settings
        QtCore.QCoreApplication.setOrganizationName("FPtje")
        QtCore.QCoreApplication.setOrganizationDomain("github.com/FPtje/gmosh")
        QtCore.QCoreApplication.setApplicationName("gmoshui")

        self.ui.settings = QtCore.QSettings()

def main():
    """Main method"""
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    initialiseUI(mySW.ui)
    mySW.show()
    sys.exit(app.exec_())

def errorMsg(s):
    """Show an error message box"""
    msgBox = QtGui.QMessageBox()
    msgBox.setText(s)
    msgBox.exec_()

class OutLog:
    """Redirect stdout to ui of program"""
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

class WorkBackground(QtCore.QThread):
    """Run something in the background"""
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

def createProgressDialog(work):
    """Create progress dialog"""
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
# Addon tools signals
#######
def addRecentAddon(widget, addon):
    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if not recentAddons: recentAddons = []
    if type(recentAddons) is str: recentAddons = [recentAddons]

    if addon in recentAddons: return False

    recentAddons.insert(0, addon)
    widget.settings.setValue("addontools/recentaddons", recentAddons)

    return True

def removeRecentAddon(widget, addon):
    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if type(recentAddons) is str: recentAddons = [recentAddons]

    recentAddons.remove(addon)
    widget.settings.setValue("addontools/recentaddons", recentAddons)

def addRecentFolderClicked(widget):
    fileName, _ = QtGui.QFileDialog.getOpenFileName(None,
        "Open addon.json file", widget.settings.value("selectAddonLastFolder", None), "addon.json files (*.json)")

    if not fileName: return

    folder, _ = os.path.split(fileName)
    # Store last used folder location
    widget.settings.setValue("selectAddonLastFolder", folder)

    if not addRecentAddon(widget, fileName): return

    item = QtGui.QStandardItem(fileName)
    item.path = fileName
    widget.recentAddons.model().insertRow(0, item)

    widget.recentAddons.selectionModel().clearSelection()
    widget.recentAddons.selectionModel().select(widget.recentAddons.model().indexFromItem(item),
        QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)

    recentFolderSelected(widget, widget.recentAddons.model().indexFromItem(item))

def removeRecentFolderClicked(widget):
    selected = widget.recentAddons.selectedIndexes()
    for s in selected:
        removeRecentAddon(widget, widget.recentAddons.model().itemFromIndex(s).path)
        widget.recentAddons.model().removeRow(s.row())

    # Select first item
    if not widget.recentAddons.model().hasIndex(0, 0): return

    firstItem = widget.recentAddons.model().index(0, 0)
    widget.recentAddons.selectionModel().select(firstItem,
        QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)

    recentFolderSelected(widget, firstItem)

def recentFolderSelected(widget, index):
    path = widget.recentAddons.model().itemFromIndex(index).path
    addonInfo = addoninfo.get_addon_info(path)

    widget.currentAddon = addonInfo

    widget.addonChangelog.setText(addonInfo.getdefault_changelog())
    widget.addonDefaultChangelog.setText(addonInfo.getdefault_changelog())
    widget.addonTitle.setText(addonInfo.gettitle())
    widget.addonIgnore.setText('\n'.join(addonInfo.getignored()))

    tags = addonInfo.gettags()

    widget.addonWorkshopid.setValue(addonInfo.getworkshopid())
    widget.addonType.setCurrentIndex(widget.addonType.findText(addonInfo.gettype()))
    widget.addonTag1.setCurrentIndex(widget.addonTag1.findText(len(tags) > 0 and tags[0] or 'None'))
    widget.addonTag2.setCurrentIndex(widget.addonTag2.findText(len(tags) > 1 and tags[1] or 'None'))
    widget.addonImage.setText(addonInfo.getlogo())

    widget.addonPublish.setEnabled(True)
    widget.addonVerify.setEnabled(True)
    widget.createGMA.setEnabled(True)
    widget.addonChangelog.setEnabled(True)
    widget.addonSave.setEnabled(True)
    widget.addonSaveAs.setEnabled(True)
    widget.addonReset.setEnabled(True)


#######
# GMA tools signals
#######
def split_path(p):
    """Helper to split a path into components"""
    a,b = os.path.split(p)
    return (split_path(a) if len(a) and len(b) else []) + [b]

def folder_hierarchy(files):
    """Helper function that creates a hierarchy of folders and files"""
    hierarchy = dict()
    hierarchy['name'] = "GMA File" + ' ' * 40
    hierarchy['children'] = dict()
    hierarchy['size'] = 0
    hierarchy['path'] = ''

    for f in files:
        split = split_path(f['name'])
        hierarchy['size'] = hierarchy['size'] + f['puresize']
        cur_h = hierarchy # Current hierarchy

        i = 0
        for sub in split:
            i = i + 1
            if not sub in cur_h['children']:
                cur_h['children'][sub] = dict()
                cur_h['children'][sub]['children'] = dict()

            cur_h = cur_h['children'][sub]
            cur_h['name'] = sub
            cur_h['path'] = '/'.join(split[0:i])
            cur_h['size'] = 'size' in cur_h and cur_h['size'] + f['puresize'] or f['puresize']

    return hierarchy


def populate(model, hierarchy, root = None):
    """Populates the GMA file tree from a hierarchy created with folder_hierarchy"""
    node = QtGui.QStandardItem(hierarchy['name'])
    size = QtGui.QStandardItem(gmafile.sizeof_simple(hierarchy['size']))
    node.filePath = size.filePath = hierarchy['path']
    root.appendRow([node, size]) if root else model.appendRow([node, size])

    for child in iter(sorted(hierarchy['children'])):
        populate(model, hierarchy['children'][child], node)

    return node

def openGmaFile(widget, fileName, error = True):
    try:
        info = gmafile.gmaInfo(fileName)
    except Exception:
        if error: errorMsg("Could not recognise the format of this file!")
        return

    widget.settings.setValue("gmatools/lastgmafile", fileName)

    widget.gmaName.setText(info['addon_name'])
    widget.gmaDescription.setText('description' in info and info['description'] or info['addon_description'])
    widget.gmaAuthor.setText(info['addon_author'])
    widget.gmaAuthorID.setValue(float(info['steamid']))
    widget.gmaTimestamp.setDateTime(QtCore.QDateTime.fromTime_t(info['timestamp']))
    widget.gmaTags.setText('tags' in info and ', '.join(info['tags']) or '')
    widget.gmaType.setText('type' in info and info['type'] or '')

    # Tree view
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(['File', 'Size'])
    widget.gmaFiles.setModel(model)

    # Fill in data
    hierarchy = folder_hierarchy(info['files'])
    root = populate(model, hierarchy)
    rootIndex = model.indexFromItem(root)
    widget.gmaFiles.resizeColumnToContents(0)

    # Expand the root node
    widget.gmaFiles.expand(rootIndex)
    # Select root node
    widget.gmaFiles.selectionModel().select(rootIndex, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)

    # Enable the extract button
    widget.gmaExtract.setEnabled(True)


def gmaSelectEdited(widget, fileName):
    openGmaFile(widget, fileName, False)

def gmaSelectEditingFinished(widget):
    openGmaFile(widget, widget.gmaSelect.text(), True)

def gmaSelectFile(widget):
    fileName, _ = QtGui.QFileDialog.getOpenFileName(None,
        "Open GMA file", widget.settings.value("selectGMALastFolder", None), "GMA files (*.gma)")

    if not fileName: return

    folder, _ = os.path.split(fileName)
    # Store last used folder location
    widget.settings.setValue("selectGMALastFolder", folder)

    widget.gmaSelect.setText(fileName)
    openGmaFile(widget, fileName)

def gmaExtract(widget):
    selected = widget.gmaFiles.selectedIndexes()
    selectedPaths = set()
    for i in selected:
        if not i.model().itemFromIndex(i).filePath: continue
        selectedPaths.add(i.model().itemFromIndex(i).filePath)

    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    destination = selectedFiles[0]
    if not selectedPaths:
        destination = os.path.join(destination, re.sub('[\\/:"*?<>|]+', '_', widget.gmaName.text()))

    createProgressDialog(
        partial(gmafile.extract, widget.gmaSelect.text(), destination, selectedPaths))

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

def wsIDEdit(widget, val):
    widget.settings.setValue("workshoptools/lastworkshopid", val)

def initRecentAddonsList(widget):
    model = QtGui.QStandardItemModel()

    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if type(recentAddons) is str: recentAddons = [recentAddons]

    widget.recentAddons.setModel(model)
    if not recentAddons: return

    for i in recentAddons:
        item = QtGui.QStandardItem(i)
        item.path = i
        model.appendRow(item)

    if recentAddons:
        widget.removeFolder.setEnabled(True)

        # Select first item
        if not widget.recentAddons.model().hasIndex(0, 0): return

        firstItem = widget.recentAddons.model().index(0, 0)
        widget.recentAddons.selectionModel().select(firstItem,
            QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)

        recentFolderSelected(widget, firstItem)


#######
# Perform startup tasks
#######
def initialiseUI(widget):
    connectMainWindowSignals(widget)

    # Addon tools init
    initRecentAddonsList(widget)

    # Gma tools init
    lastGMA = widget.settings.value("gmatools/lastgmafile", '')
    widget.gmaSelect.setText(lastGMA)
    openGmaFile(widget, lastGMA, False)

    # Workshop tools init
    widget.wsID.setValue(float(widget.settings.value("workshoptools/lastworkshopid", 0)))

#######
# Connect all signals
#######
def connectMainWindowSignals(widget):
    # Addon tools signals
    widget.addFolder.clicked.connect(partial(addRecentFolderClicked, widget))
    widget.removeFolder.clicked.connect(partial(removeRecentFolderClicked, widget))
    widget.recentAddons.clicked.connect(partial(recentFolderSelected, widget))

    # GMA tools signals
    widget.gmaSelectFile.clicked.connect(partial(gmaSelectFile, widget))
    widget.gmaExtract.clicked.connect(partial(gmaExtract, widget))
    widget.gmaSelect.textEdited.connect(partial(gmaSelectEdited, widget))
    widget.gmaSelect.returnPressed.connect(partial(gmaSelectEditingFinished, widget))

    # Workshop signals
    widget.wsGetInfo.clicked.connect(partial(wsGetInfoClicked, widget))
    widget.wsDownload.clicked.connect(partial(wsDownloadClicked, widget))
    widget.wsID.valueChanged.connect(partial(wsIDEdit, widget))


try:
    if __name__ == '__main__': main()
except KeyboardInterrupt: pass
