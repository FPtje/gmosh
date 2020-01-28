#!/usr/bin/env python3
"""Starts the user interface of gmoshui."""

from _version import __version__
from PySide2 import QtCore, QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QFile
from functools import partial
import workshoputils
import addoninfo
import gmpublish
import gmafile
import sys
import shiboken2 as shiboken
import os
import re
from gmodfolder import GModFolder

def main():
    """Main method"""
    app = QApplication(sys.argv)
    
    loader = QUiLoader()
    
    mainwindow_ui_file = QFile(os.path.abspath("ui/mainwindow.ui"))
    mainwindow_ui_file.open(QFile.ReadOnly)
    
    mainwindow = loader.load(mainwindow_ui_file)
    mainwindow_ui_file.close()
    
    progressdialog_ui_file = QFile(os.path.abspath("ui/progressdialog.ui"))
    progressdialog_ui_file.open(QFile.ReadOnly)

    global progressdialog
    progressdialog = loader.load(progressdialog_ui_file)
    progressdialog_ui_file.close()
    
    mainwindow.setWindowTitle("GMosh UI " + __version__)

    # Create settings
    QtCore.QCoreApplication.setOrganizationName("FPtje")
    QtCore.QCoreApplication.setOrganizationDomain("github.com/FPtje/gmosh")
    QtCore.QCoreApplication.setApplicationName("gmoshui")

    mainwindow.settings = QtCore.QSettings()

    initialiseUI(mainwindow)
    mainwindow.show()
    sys.exit(app.exec_())


def errorMsg(s):
    """Show an error message box"""
    msgBox = QMessageBox()
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

    def flush(x):
        pass

class WorkBackground(QtCore.QThread):
    """Run something in the background"""
    target = id
    signal = QtCore.Signal(str)
    finished = QtCore.Signal()
    def run(self):
        oldstdout = sys.stdout
        sys.stdout = OutLog(self.signal, sys.stdout)

        self.result = self.target()
        self.signal.emit("<br /><h3>FINISHED</h3>")

        sys.stdout = oldstdout
        self.finished.emit()

def createProgressDialog(work, onresult=id):
    """Create progress dialog"""
    dialog = QDialog()
    ui = progressdialog

    def onThreadOutput(text):
        if not shiboken.isValid(ui) or not shiboken.isValid(ui.progressText): return

        ui.progressText.moveCursor(QTextCursor.End)
        if text[0] == "\r":
            #cursor = QTextCursor(ui.progressText.textCursor())
            ui.progressText.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            ui.progressText.moveCursor(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)

        ui.progressText.insertHtml(text.replace('\n', '<br />'))

    def enableButtons():
        ui.buttonBox.setEnabled(True)
        onresult(thread.result)

    thread = WorkBackground()
    thread.target = work
    thread.signal.connect(onThreadOutput)
    thread.finished.connect(enableButtons)
    thread.start()

    dialog.show()
    dialog.exec_()
    thread.exit()
    del thread

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

def moveRecentAddon(widget, fr, to):
    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if type(recentAddons) is str: recentAddons = [recentAddons]

    recentAddons.insert(to, recentAddons.pop(fr))

    widget.settings.setValue("addontools/recentaddons", recentAddons)

illegalFilesFoundMessage = """\
<h1>Illegal files found!</h1>
<p>The addon contains some files that are not allowed to be in a GMA file.</p>
<p>These are the illegal files:</p>

%s

<p>It is recommended to either remove those files or to copy paste the above list in the "Files to ignore" box</p>
"""
def addonVerifyClicked(widget, show_ok = True):
    verified, badlist = widget.currentAddon.verify_files()
    if verified:
        if show_ok: errorMsg("No illegal files were found. You're good to go!")
        return True

    dialog = QDialog()
    ui = progressdialog.Ui_Dialog()
    ui.setupUi(dialog)
    ui.progressText.setText(illegalFilesFoundMessage % '<br />'.join(badlist))
    ui.buttonBox.setEnabled(True)
    dialog.show()
    dialog.exec_()

    return False

def addonCreateGMAClicked(widget):
    fileName, _ = QFileDialog.getSaveFileName(None,
        "Store GMA file", os.path.join(widget.settings.value("addontools/lastgmafolder", ''), 'out.gma'), "GMA files (*.gma)")

    if not fileName: return
    # Force .gma extension
    fileName = os.path.splitext(fileName)[0] + '.gma'
    folder, _ = os.path.split(fileName)

    # Store last used folder location
    widget.settings.setValue("addontools/lastgmafolder", folder)

    # Verify the addon
    if not addonVerifyClicked(widget, False): return

    createProgressDialog(partial(widget.currentAddon.compress, fileName))

def publishNew(widget, publisher):
    succeeded, output = publisher.create()
    if succeeded:
        widget.currentAddon.save_changes()
        print("<h1>Upload succeeded!</h1><br />")
        print("<p>The addon has been uploaded. Do check it out at </p>")
        print('<a href="http://steamcommunity.com/sharedfiles/filedetails/?id=%s">http://steamcommunity.com/sharedfiles/filedetails/?id=%s</a>' % (output, output))
        print("<br /><p>Note that you will have to change the visibility of this addon in the above link to make it visible for everyone.</p>")
        return

    print("<h1>Upload failed!</h1> <br />")
    print("<p>The upload has failed! The error message can be read below:</p><br />")
    print("<br /><tt>")
    print(output)
    print("</tt>")

def addonPublishClicked(widget):
    if not widget.currentAddon.has_workshop_id() and not widget.currentAddon.getlogo():
        errorMsg("Error: When uploading a new addon to the workshop, a 512x512 jpeg image must be given.\n"
                 "Please either enter a workshop id or provide a 512x512 jpeg image.")
        return

    if not addonVerifyClicked(widget, False): return

    changelog = widget.addonChangelog.toPlainText() or widget.currentAddon.getdefault_changelog() or ''

    publisher = gmpublish.GmPublish(widget.currentAddon)

    if widget.currentAddon.has_workshop_id():
        createProgressDialog(partial(publisher.update, changelog))
        return

    ok = QMessageBox.warning(None, "Upload new addon", "This will be uploaded as a new addon on the workshop. To update an existing addon, please fill in the workshop ID of that addon. Are you sure you want to upload this addon?", QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes

    if not ok: return

    createProgressDialog(partial(publishNew, widget, publisher))

def moveSelectedRecentAddon(widget, direction):
    selected = widget.recentAddons.selectedIndexes()
    for s in selected:
        rowText = s.data()
        path = widget.recentAddons.model().itemFromIndex(s).path

        item = QStandardItem(rowText)
        item.path = path

        widget.recentAddons.model().removeRow(s.row())
        widget.recentAddons.model().insertRow(s.row() + direction, item)

        widget.recentAddons.selectionModel().clearSelection()
        widget.recentAddons.selectionModel().select(widget.recentAddons.model().indexFromItem(item),
            QItemSelectionModel.Select | QItemSelectionModel.Rows)

        moveRecentAddon(widget, s.row(), s.row() + direction)
        break

    enableRecentAddonsUpDownButtons(widget)

def addonMoveUpClicked(widget):
    moveSelectedRecentAddon(widget, -1)

def addonMoveDownClicked(widget):
    moveSelectedRecentAddon(widget, 1)

def addRecentFolderClicked(widget):
    fileName, _ = QFileDialog.getOpenFileName(None,
        "Open addon.json file", widget.settings.value("selectAddonLastFolder", None), "addon.json files (*.json)")

    if not fileName: return

    folder, _ = os.path.split(fileName)
    # Store last used folder location
    widget.settings.setValue("selectAddonLastFolder", folder)

    try:
        addoninfo.get_addon_info(fileName)
    except Exception:
        errorMsg("%s does not contain valid json!" % fileName)
        return

    if not addRecentAddon(widget, fileName): return

    item = QStandardItem(shortenPath(fileName))
    item.path = fileName
    widget.recentAddons.model().insertRow(0, item)

    widget.recentAddons.selectionModel().clearSelection()
    widget.recentAddons.selectionModel().select(widget.recentAddons.model().indexFromItem(item),
        QItemSelectionModel.Select | QItemSelectionModel.Rows)

    recentFolderSelected(widget, widget.recentAddons.model().indexFromItem(item))

def removeRecentFolderClicked(widget):
    selected = widget.recentAddons.selectedIndexes()
    for s in selected:
        removeRecentAddon(widget, widget.recentAddons.model().itemFromIndex(s).path)
        widget.recentAddons.model().removeRow(s.row())

    # Select first item
    if not widget.recentAddons.model().hasIndex(0, 0): return

    widget.recentAddons.selectionModel().clearSelection()
    firstItem = widget.recentAddons.model().index(0, 0)
    widget.recentAddons.selectionModel().select(firstItem,
        QItemSelectionModel.Select | QItemSelectionModel.Rows)

    recentFolderSelected(widget, firstItem)

def recentFolderSelected(widget, index):
    enableRecentAddonsUpDownButtons(widget)
    path = widget.recentAddons.model().itemFromIndex(index).path

    try:
        addonInfo = addoninfo.get_addon_info(path)
    except Exception:
        return

    widget.currentAddon = addonInfo or addoninfo.GModAddon(dict(), '.')

    if not addonInfo: return

    widget.addonChangelog.setText(addonInfo.getdefault_changelog())
    widget.addonDefaultChangelog.setText(addonInfo.getdefault_changelog())
    widget.addonTitle.setText(addonInfo.gettitle())
    widget.addonDescription.setText(addonInfo.getdescription())
    widget.addonIgnore.setText('\n'.join(addonInfo.getignored()))

    tags = addonInfo.gettags()

    widget.addonWorkshopid.setValue(addonInfo.getworkshopid())
    widget.addonType.setCurrentIndex(widget.addonType.findText(addonInfo.gettype()))
    widget.addonTag1.setCurrentIndex(widget.addonTag1.findText(len(tags) > 0 and tags[0] or 'None'))
    widget.addonTag2.setCurrentIndex(widget.addonTag2.findText(len(tags) > 1 and tags[1] or 'None'))
    widget.addonImage.setText(addonInfo.getlogo())

    widget.addonPublish.setEnabled(True)
    widget.addonVerify.setEnabled(True)
    widget.addonCreateGMA.setEnabled(True)
    widget.addonChangelog.setEnabled(True)
    widget.addonSave.setEnabled(True)
    widget.addonSaveAs.setEnabled(True)
    widget.addonReset.setEnabled(True)

def addonSaveClicked(widget):
    widget.currentAddon.save_changes()

def addonSaveAsClicked(widget):
    fileName, _ = QFileDialog.getSaveFileName(None,
        "Store addon.json file", os.path.join(widget.settings.value("addontools/lastsaveasfolder", ''), 'addon.json'), "json files (*.json)")

    if not fileName: return
    # Force .json extension
    fileName = os.path.splitext(fileName)[0] + '.json'
    folder, _ = os.path.split(fileName)

    # Store last used folder location
    widget.settings.setValue("addontools/lastsaveasfolder", folder)

    widget.currentAddon.setfile(fileName)
    widget.currentAddon.save_changes()
    if not addRecentAddon(widget, fileName): return

    # Add to recent addons list
    item = QStandardItem(shortenPath(fileName))
    item.path = fileName
    widget.recentAddons.model().insertRow(0, item)

    widget.recentAddons.selectionModel().clearSelection()
    widget.recentAddons.selectionModel().select(widget.recentAddons.model().indexFromItem(item),
        QItemSelectionModel.Select | QItemSelectionModel.Rows)

def addonResetClicked(widget):
    selected = widget.recentAddons.selectedIndexes()
    for s in selected:
        recentFolderSelected(widget, s)
        break

def updateAddonInfo(widget, key, target, fnvalue, *args):
    value = fnvalue(target) if callable(fnvalue) else fnvalue

    if not value:
        if key in widget.currentAddon.data:
            widget.currentAddon.data.pop(key)
    else:
        widget.currentAddon.data[key] = value

def updateAddonTags(widget, val):
    tag1 = widget.addonTag1.currentText()
    tag2 = widget.addonTag2.currentText()

    tags = []
    if tag1 and tag1 != 'None': tags.append(tag1)
    if tag2 and tag2 != 'None': tags.append(tag2)

    widget.currentAddon.data['tags'] = tags

def selectAddonImage(widget):
    fileName, _ = QFileDialog.getOpenFileName(None,
        "Open jpg file", widget.settings.value("addontools/lastlogofolder", None), "jpeg files (*.jpg *.jpeg)")

    if not fileName: return

    folder, _ = os.path.split(fileName)
    # Store last used folder location
    widget.settings.setValue("addontools/lastlogofolder", folder)

    widget.addonImage.setText(fileName)
    widget.currentAddon.data['logo'] = fileName

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
    node = QStandardItem(hierarchy['name'])
    size = QStandardItem(gmafile.sizeof_simple(hierarchy['size']))
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
    model = QStandardItemModel()
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
    widget.gmaFiles.selectionModel().select(rootIndex, QItemSelectionModel.Select | QItemSelectionModel.Rows)

    # Enable the extract button
    widget.gmaExtract.setEnabled(True)
    widget.gmaOpen.setEnabled(True)


def gmaSelectEdited(widget, fileName):
    openGmaFile(widget, fileName, False)

def gmaSelectEditingFinished(widget):
    openGmaFile(widget, widget.gmaSelect.text(), True)

def gmaSelectFile(widget):
    fileName, _ = QFileDialog.getOpenFileName(None,
        "Open GMA file", widget.settings.value("selectGMALastFolder", None), "GMA files (*.gma)")

    if not fileName: return

    folder, _ = os.path.split(fileName)
    # Store last used folder location
    widget.settings.setValue("selectGMALastFolder", folder)

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

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    destination = selectedFiles[0]
    if not selectedPaths:
        destination = os.path.join(destination, re.sub('[\\/:"*?<>|]+', '_', widget.gmaName.text()))

    createProgressDialog(
        partial(gmafile.extract, widget.gmaSelect.text(), destination, selectedPaths))

def gmaOpen(widget):
    selected = widget.gmaFiles.selectedIndexes()
    selectedPaths = set()
    for i in selected:
        if not i.model().itemFromIndex(i).filePath: continue
        selectedPaths.add(i.model().itemFromIndex(i).filePath)

    createProgressDialog(
        partial(gmafile.openFiles, widget.gmaSelect.text(), selectedPaths))

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
    if not 'title' in info:
        errorMsg("Unable to retrieve addon info. Make sure the workshop ID is correct.")
        return

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
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    workshopid = widget.wsID.value()
    extract = widget.wsExtract.isChecked()
    def work():
        workshoputils.download([workshopid], selectedFiles[0], extract)

    createProgressDialog(work)

def wsIDEdit(widget, val):
    widget.settings.setValue("workshoptools/lastworkshopid", val)


def lcacheSetGmodDirClicked(widget):
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    widget.gmodfolder.path = selectedFiles[0]
    if not widget.gmodfolder.get_cache_folder():
        errorMsg("This does not look like a correct gmod folder.")
        lcacheSetGmodDirClicked(widget)
        return

    widget.settings.setValue("lcache/gmoddir", widget.gmodfolder.path)

    setupLuaCacheView(widget)

def lcacheFileSelected(widget, selected):
    ix = selected.indexes()[-1]
    path = widget.lcacheTree.model().filePath(ix)
    text = widget.gmodfolder.extract_cache_file(path).decode('utf-8', 'replace')
    if widget.lcacheSearchField.text():
        try:
            pattern = re.compile('(%s)' % widget.lcacheSearchField.text())
            text = re.sub(pattern, r'<b><u>\1</u></b>', text)
        except:
            pass

    widget.lcacheContents.setHtml('<pre>%s</pre>' % text)

def lcacheExtractClicked(widget):
    selected = widget.lcacheTree.selectedIndexes()

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    items = set()
    for s in selected:
        items.add(os.path.normpath(widget.lcacheTree.model().filePath(s)))

    widget.gmodfolder.extract_cache_files(selectedFiles[0], items)

def lcacheExtractAllClicked(widget):
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly)
    if not dialog.exec_(): return
    selectedFiles = dialog.selectedFiles()

    createProgressDialog(
        partial(widget.gmodfolder.extract_cache_files, os.path.normpath(selectedFiles[0])))

def lcacheSearch(widget):
    query = widget.lcacheSearchField.text()

    def onFinished(matches):
        matches = matches or ['\0']
        widget.lcacheTree.model().setNameFilters(matches)

    createProgressDialog(
        partial(widget.gmodfolder.search_cache, query),
        onFinished
        )

def lcacheSearchFieldEdited(widget, txt):
    lcacheFileSelected(widget, widget.lcacheTree.selectedThings)

def shortenPath(path, maxI = 4):
    """Simple function that shortens path names"""
    res = []

    l, r = os.path.split(path)
    for i in range(0, maxI):
        l, r = os.path.split(path)
        res.append(r)
        path = l

    res.append('...')
    l, r = os.path.splitdrive(path)
    res.append(l)

    return '/'.join(list(reversed(res)))

def enableRecentAddonsUpDownButtons(widget):
    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if type(recentAddons) is str: recentAddons = [recentAddons]

    selected = widget.recentAddons.selectedIndexes()

    widget.addonMoveUp.setEnabled(True)
    widget.addonMoveDown.setEnabled(True)
    if not recentAddons or len(selected) > 1:
        widget.addonMoveUp.setEnabled(False)
        widget.addonMoveDown.setEnabled(False)
        return

    for s in selected:
        if s.row() == 0:
            widget.addonMoveUp.setEnabled(False)
        if s.row() == len(recentAddons) - 1:
            widget.addonMoveDown.setEnabled(False)

def initRecentAddonsList(widget):
    model = QStandardItemModel()

    recentAddons = widget.settings.value("addontools/recentaddons", [])
    if type(recentAddons) is str: recentAddons = [recentAddons]

    widget.recentAddons.setModel(model)
    if not recentAddons: return

    for i in recentAddons:
        item = QStandardItem(shortenPath(i))
        item.path = i
        model.appendRow(item)

    if recentAddons:
        widget.removeFolder.setEnabled(True)

        # Select first item
        if not widget.recentAddons.model().hasIndex(0, 0): return

        firstItem = widget.recentAddons.model().index(0, 0)
        widget.recentAddons.selectionModel().select(firstItem,
            QItemSelectionModel.Select | QItemSelectionModel.Rows)

        recentFolderSelected(widget, firstItem)

def setupLuaCacheView(widget):
    if not widget.gmodfolder.path:
        return

    model = QFileSystemModel()
    widget.lcacheTree.setModel(model)

    model.setNameFilterDisables(False)

    cachedir = widget.gmodfolder.get_cache_folder()
    widget.lcacheTree.setRootIndex(model.setRootPath(cachedir))
    widget.lcacheTree.setSortingEnabled(True)
    widget.lcacheTree.header().hideSection(2) # hide file type column

#######
# Perform startup tasks
#######
def initialiseUI(widget):
    widget.currentAddon = addoninfo.GModAddon(dict(), '.')
    
    # Addon tools init
    initRecentAddonsList(widget)

    # Gma tools init
    lastGMA = widget.settings.value("gmatools/lastgmafile", '')
    widget.gmaSelect.setText(lastGMA)
    openGmaFile(widget, lastGMA, False)

    # Workshop tools init
    widget.wsID.setValue(float(widget.settings.value("workshoptools/lastworkshopid", 0)))

    if len(sys.argv) > 1:
        gmaFile = os.path.abspath(sys.argv[1])
        widget.gmaSelect.setText(gmaFile)
        openGmaFile(widget, gmaFile, False)
        widget.tabWidget.setCurrentIndex(1)

    # Lua cache init
    widget.gmodfolder = GModFolder(widget.settings.value("lcache/gmoddir", None))

    if not widget.gmodfolder.get_cache_folder() and not widget.gmodfolder.find_gmod_folder():
        return

    widget.settings.setValue("lcache/gmoddir",
        widget.settings.value("lcache/gmoddir", widget.gmodfolder.path))
    setupLuaCacheView(widget)
    
    connectMainWindowSignals(widget)


#######
# Connect all signals
#######
def connectMainWindowSignals(widget):
    # Addon tools signals
    widget.addonVerify.clicked.connect(partial(addonVerifyClicked, widget))
    widget.addonCreateGMA.clicked.connect(partial(addonCreateGMAClicked, widget))
    widget.addonPublish.clicked.connect(partial(addonPublishClicked, widget))
    widget.addonMoveUp.clicked.connect(partial(addonMoveUpClicked, widget))
    widget.addonMoveDown.clicked.connect(partial(addonMoveDownClicked, widget))
    widget.addFolder.clicked.connect(partial(addRecentFolderClicked, widget))
    widget.removeFolder.clicked.connect(partial(removeRecentFolderClicked, widget))
    widget.recentAddons.clicked.connect(partial(recentFolderSelected, widget))
    widget.addonSave.clicked.connect(partial(addonSaveClicked, widget))
    widget.addonSaveAs.clicked.connect(partial(addonSaveAsClicked, widget))
    widget.addonReset.clicked.connect(partial(addonResetClicked, widget))
    # Update addon info:
    widget.addonTitle.textEdited.connect(
        partial(updateAddonInfo, widget, 'title', widget.addonTitle)
    )
    widget.addonDescription.textChanged.connect(
        partial(updateAddonInfo, widget, 'description', widget.addonDescription, QTextEdit.toPlainText)
    )
    widget.addonDefaultChangelog.textChanged.connect(
        partial(updateAddonInfo, widget, 'default_changelog', widget.addonDefaultChangelog, QTextEdit.toPlainText)
    )
    widget.addonImage.textEdited.connect(
        partial(updateAddonInfo, widget, 'logo', widget.addonImage)
    )
    widget.addonWorkshopid.valueChanged.connect(
        partial(updateAddonInfo, widget, 'workshopid', widget.addonWorkshopid)
    )
    widget.addonIgnore.textChanged.connect(
        partial(updateAddonInfo, widget, 'ignore', widget.addonIgnore,
            # Filter out empty strings
            lambda x: list(filter(bool, x.toPlainText().split('\n'))))
    )
    widget.addonType.currentIndexChanged.connect(
        partial(updateAddonInfo, widget, 'type', widget.addonType,
            lambda x: x.currentText())
    )
    widget.addonTag1.currentIndexChanged.connect(partial(updateAddonTags, widget))
    widget.addonTag2.currentIndexChanged.connect(partial(updateAddonTags, widget))
    widget.addonImageBrowse.clicked.connect(partial(selectAddonImage, widget))

    # GMA tools signals
    widget.gmaSelectFile.clicked.connect(partial(gmaSelectFile, widget))
    widget.gmaExtract.clicked.connect(partial(gmaExtract, widget))
    widget.gmaOpen.clicked.connect(partial(gmaOpen, widget))
    widget.gmaSelect.textEdited.connect(partial(gmaSelectEdited, widget))
    widget.gmaSelect.returnPressed.connect(partial(gmaSelectEditingFinished, widget))

    # Workshop signals
    widget.wsGetInfo.clicked.connect(partial(wsGetInfoClicked, widget))
    widget.wsDownload.clicked.connect(partial(wsDownloadClicked, widget))
    widget.wsID.valueChanged.connect(partial(wsIDEdit, widget))

    # Lua cache signals
    widget.lcacheSetGmodDir.clicked.connect(partial(lcacheSetGmodDirClicked, widget))
    widget.lcacheExtract.clicked.connect(partial(lcacheExtractClicked, widget))
    widget.lcacheExtractAll.clicked.connect(partial(lcacheExtractAllClicked, widget))
    widget.lcacheSearchButton.clicked.connect(partial(lcacheSearch, widget))

    def sChanged(selected, deselected):
        lcacheFileSelected(widget, selected)
        widget.lcacheTree.selectedThings = selected

    widget.lcacheTree.selectionModel().selectionChanged.connect(sChanged)
    widget.lcacheSearchField.textEdited.connect(partial(lcacheSearchFieldEdited, widget))

try:
    if __name__ == '__main__': main()
except KeyboardInterrupt: pass
