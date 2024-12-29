from PyQt5.QtCore import (QPoint, QSettings, QSignalMapper,
        QSize, Qt)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
        QMdiArea, QMessageBox, QWidget)
from cdr import CDRBlob
from gui_stuff.apprecord_view import AppRecordWindow
from gui_stuff.info_view import InfoWindow
from gui_stuff.subscription_view import SubscriptionRecordWindow

class MainWindow(QMainWindow):
    def __init__(self):
        self.blob = None
        super(MainWindow, self).__init__()
        self.mdi_area = QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)
        self.wnd_mapper = QSignalMapper(self)
        self.wnd_mapper.mapped[QWidget].connect(self.setActiveSubWindow)
        self.statusBar().showMessage("Ready")

        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.load_settings()
        self.setWindowTitle(">_<")
        self.setWindowIcon(QIcon("./icons/rainbow.png"))

    #MANAGED BY QSIGNALMAPPER
    def closeEvent(self, event):
        self.mdi_area.closeAllSubWindows()
        if self.mdi_area.currentSubWindow():
            event.ignore()
        else:
            self.write_settings()
            event.accept()
    
    def error_msgbox(self, title : str, content :str, fn : callable = None) -> QMessageBox:
        msg = QMessageBox(self)
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.setIconPixmap(QIcon("./icons/error.png").pixmap(QSize(128,128)))
        msg.setWindowIcon(QIcon("./icons/exclamation.png"))
        msg.setAttribute(Qt.WA_DeleteOnClose)
        msg.show()
        msg.exec()
        return

    def open(self):
        filename, _ = QFileDialog.getOpenFileName(self)
        if filename == "":
            return
        if self.blob:
            self.error_msgbox("Message","You have to unload the blob before loading another")
            return
        try:
            self.blob = CDRBlob.from_file(filename)
            self.statusBar().showMessage(f"Blob loaded, version {self.blob.VersionNumber}", 2000)
            return
        except Exception as e:
            self.error_msgbox("Failed!", f"Exception: {e}")
            self.statusBar().showMessage(f"Failed to load the file!", 2000)

    def close_blob(self):
        if self.blob:
            self.mdi_area.closeAllSubWindows()
            self.blob = None
            self.statusBar().showMessage(f"Blob unloaded!", 2000)
        else:
            self.statusBar().showMessage(f"Can't unload a blob without one loaded", 2000)
    def about(self):
        QMessageBox.about(self, "About >_<",
                "meow mewo meoww mrow mrr meow meow meow mrrp mrow meow mrow meow meow mrrp ")

    def is_loaded(self):
        if not self.blob:
            self.error_msgbox("No blob loaded", "Load a blob first", self.open)
            return False
        return True

    def update_window_menu(self):
        self.wnd_menu.clear()
        self.wnd_menu.addAction(self.close_action)
        self.wnd_menu.addAction(self.closeall_action)
        self.wnd_menu.addSeparator()
        self.wnd_menu.addAction(self.tile_action)
        self.wnd_menu.addAction(self.cascade_action)
        self.wnd_menu.addSeparator()
        self.wnd_menu.addAction(self.next_action)
        self.wnd_menu.addAction(self.previous_action)
        self.wnd_menu.addAction(self.separator_action)

        windows = self.mdi_area.subWindowList()
        self.separator_action.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.wnd_name())
            if i < 9:
                text = '&' + text

            action = self.wnd_menu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.active_child())
            action.triggered.connect(self.wnd_mapper.map)
            self.wnd_mapper.setMapping(action, window)

    def create_actions(self):

        self.open_action = QAction(QIcon('./icons/folder_page.png'), "&Open...", self,
                shortcut=QKeySequence.Open, statusTip="Open a blob file",
                triggered=self.open)

        self.closeblob_action = QAction(QIcon('./icons/folder_delete.png'), "&Unload blob...", self,
                statusTip="Unload the blob file",
                triggered=self.close_blob)

        self.exit_action = QAction(QIcon('./icons/cross.png'), "E&xit", self, shortcut=QKeySequence.Quit,
                statusTip="Exit the application",
                triggered=QApplication.instance().closeAllWindows)

        self.close_action = QAction(QIcon('./icons/application_delete.png'),"Cl&ose", self,
                statusTip="Close the active window",
                triggered=self.mdi_area.closeActiveSubWindow)

        self.closeall_action = QAction(QIcon('./icons/application_delete.png'),"Close &All", self,
                statusTip="Close all the windows",
                triggered=self.mdi_area.closeAllSubWindows)

        self.tile_action = QAction(QIcon('./icons/application_tile_horizontal.png'), "&Tile", self, statusTip="Tile the windows",
                triggered=self.mdi_area.tileSubWindows)

        self.cascade_action = QAction(QIcon('./icons/application_cascade.png'), "&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.mdi_area.cascadeSubWindows)

        self.next_action = QAction(QIcon("./icons/arrow_right.png"), "Ne&xt", self, shortcut=QKeySequence.NextChild,
                statusTip="Move the focus to the next window",
                triggered=self.mdi_area.activateNextSubWindow)

        self.previous_action = QAction(QIcon("./icons/arrow_left.png"), "Pre&vious", self,
                shortcut=QKeySequence.PreviousChild,
                statusTip="Move the focus to the previous window",
                triggered=self.mdi_area.activatePreviousSubWindow)

        self.separator_action = QAction(self)
        self.separator_action.setSeparator(True)

        self.viewapprecord_action = QAction(QIcon('./icons/table.png'), "View Application Record", self, statusTip="View Application Record Entries", triggered=self.open_apprecord_view)
        self.viewinfo_action = QAction(QIcon('./icons/information.png'), "Blob Info", self, statusTip="View embedded blob information", triggered=self.open_info_view)
        self.viewsubscriptions_action = QAction(QIcon('./icons/cart.png'), "View Subscription Record", self, statusTip="View Subscription Record Entries", triggered=self.open_subrecord_view)

        self.about_action = QAction(QIcon('./icons/information.png'), "&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQt_action = QAction(QIcon('./icons/information.png'), "About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QApplication.instance().aboutQt)

    def create_menus(self):
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        action = self.file_menu.addAction(QIcon('./icons/arrow_switch.png'), "Switch layout direction")
        action.triggered.connect(self.switch_layout)
        self.file_menu.addAction(self.exit_action)

        self.blob_menu = self.menuBar().addMenu("&Blob")
        self.blob_menu.addAction(self.open_action)
        self.blob_menu.addAction(self.closeblob_action)
        self.blob_menu.addAction(self.viewapprecord_action)
        self.blob_menu.addAction(self.viewsubscriptions_action)
        self.blob_menu.addAction(self.viewinfo_action)



        self.wnd_menu = self.menuBar().addMenu("&Window")
        self.update_window_menu()
        self.wnd_menu.aboutToShow.connect(self.update_window_menu)

        self.menuBar().addSeparator()

        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.about_action)
        self.help_menu.addAction(self.aboutQt_action)

    def create_toolbars(self):
        self.main_toolbar = self.addToolBar("File")
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.closeblob_action)
        self.main_toolbar.addAction(self.viewapprecord_action)
        self.main_toolbar.addAction(self.viewsubscriptions_action)

        self.main_toolbar.addAction(self.viewinfo_action)
        

    # open_*

    def open_apprecord_view(self):
        if not self.is_loaded():
            return
        
        apprecord_window = AppRecordWindow(self.blob.ApplicationRecord, self.mdi_area)
        self.mdi_area.addSubWindow(apprecord_window)
        apprecord_window.show()

    def open_info_view(self):
        if not self.is_loaded():
            return
        
        infowindow = InfoWindow(self.blob.VersionNumber, self.blob.LastChangedExistingAppOrSubscriptionTime)
        self.mdi_area.addSubWindow(infowindow)
        infowindow.show()

    def open_subrecord_view(self):
        if not self.is_loaded():
            return

        subrecordwindow = SubscriptionRecordWindow(self.blob, self.mdi_area)
        self.mdi_area.addSubWindow(subrecordwindow)
        subrecordwindow.show()

    def load_settings(self):
        settings = QSettings('btsblobviewer', 'blobviewer')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def write_settings(self):
        settings = QSettings('btsblobviewer', 'blobviewer')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def active_child(self):
        activeSubWindow = self.mdi_area.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def switch_layout(self):
        if self.layoutDirection() == Qt.LeftToRight:
            QApplication.setLayoutDirection(Qt.RightToLeft)
        else:
            QApplication.setLayoutDirection(Qt.LeftToRight)

    def setActiveSubWindow(self, window):
        if window:
            self.mdi_area.setActiveSubWindow(window)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
