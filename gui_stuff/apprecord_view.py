from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (
        QMdiArea, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QAbstractItemView)
from cdr import BaseMapParser
from gui_stuff.utl_widgets import CDRListViewListWidgetItem, CDRListViewWindow, copy_to_clipboard

class AppRecordWindow(QWidget):

    def on_table_click(self, item):
        if isinstance(item, CDRListViewListWidgetItem):
            wnd = CDRListViewWindow(item.ctx_tbl)
            self.mdiarea.addSubWindow(wnd)
            wnd.show()
            return
        
        if isinstance(item, QTableWidgetItem):
            copy_to_clipboard(item.text())

    def populate_table(self):
        fields = [
            "AppId",
            "Name",
            "InstallDirName",
            "MinCacheFileSizeMB",
            "MaxCacheFileSizeMB",
            "LaunchOptionsRecord",
            "AppIconsRecord",
            "OnFirstLaunch",
            "IsBandwidthGreedy",
            "VersionsRecord",
            "CurrentVersionId",
            "FilesystemsRecord",
            "TrickleVersionId",
            "UserDefinedRecord",
            "BetaVersionPassword",
            "BetaVersionId",
            "LegacyInstallDirName",
            "SkipMFPOverwrite",
            "UseFilesystemDvr",
            "ManifestOnlyApp",
            "AppOfManifestOnlyCache",
            "RegionSpecificRecord"
        ]

        nametoid = {
            "AppId" : 0,
            "Name" : 1,
            "InstallDirName" : 2,
            "MinCacheFileSizeMB" :3,
            "MaxCacheFileSizeMB" :4,
            "LaunchOptionsRecord": 5,
            "AppIconsRecord" :6,
            "OnFirstLaunch" :7 ,
            "IsBandwidthGreedy": 8,
            "VersionsRecord": 9,
            "CurrentVersionId": 10,
            "FilesystemsRecord" : 11,
            "TrickleVersionId" : 12,
            "UserDefinedRecord": 13,
            "BetaVersionPassword" : 14,
            "BetaVersionId" : 15,
            "LegacyInstallDirName" : 16,
            "SkipMFPOverwrite": 17,
            "UseFilesystemDvr": 18,
            "ManifestOnlyApp" : 19,
            "AppOfManifestOnlyCache" : 20,
            "RegionSpecificRecord" : 21,
        }

        self.main_table.setRowCount(len(self.cdr.dict()))
        self.main_table.setColumnCount(len(fields)-1)

        self.main_table.setHorizontalHeaderLabels(fields[1:])
        self.sorted_dict = {str(k): v for k, v in sorted(self.cdr.dict().items(), key=lambda item: item[1].AppId)}
        self.main_table.setVerticalHeaderLabels(self.sorted_dict.keys())
        i = 0
        for v in self.sorted_dict.values():
            for kk,vv in vars(v).items():
                if kk == "AppId":
                    continue
                
                if isinstance(vv, BaseMapParser):                 
                    if len(vv.dict()) != 0:
                        self.main_table.setItem(i,nametoid[kk]-1, CDRListViewListWidgetItem("Click to view", vv))
                    else:
                        self.main_table.setItem(i,nametoid[kk]-1, QTableWidgetItem("n/a"))
                    continue
                self.main_table.setItem(i,nametoid[kk]-1, QTableWidgetItem(str(vv)))
            i += 1

    def __init__(self, cdr_dict : dict, mdiarea : QMdiArea):
        self.cdr = cdr_dict
        self.mdiarea = mdiarea
        super(AppRecordWindow, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        #self.setWindowIcon(QIcon("./icons/database_table.png"));

        self.setWindowTitle("Application Record")
        self.resize(500,500)

        self.main_table = QTableWidget()
        self.main_table.itemDoubleClicked.connect(self.on_table_click)
        self.main_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.populate_table()
        self.layout = QVBoxLayout() 
        self.layout.addWidget(self.main_table)
        self.setLayout(self.layout) 
    
    def wnd_name(self):
        return "Application Record"
