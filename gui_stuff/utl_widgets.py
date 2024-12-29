from cdr import BaseMapParser, BaseParser, UserDefinedRecord
from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (
        QWidget, QTableWidgetItem, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QListWidget, QApplication)

def copy_to_clipboard(content :str) -> None:
    cb = QApplication.clipboard()
    cb.clear()
    cb.setText(content)

class CDRListViewWindow(QWidget):

    def pretty_root_name(self, item):

        base = item.__class__.__name__

        if item.__class__.__name__ == "VersionsRecord":
                return f"{base} (v{item.VersionId})"
        
        if base == "LaunchOptionsRecord":
                return base
        
        if base == "FilesystemRecord":
                return f"{base} app {item.AppId}"
        return base
    def populate_tree(self):
        items = []

        if isinstance(self.lst, UserDefinedRecord):
            items = []
            for k,v in self.lst.dict().items():
                items.append(QTreeWidgetItem([str(k), str(v)]))
            self.main_table.insertTopLevelItems(0,items)
            return

        for i in self.lst.dict().values():
            item = QTreeWidgetItem([self.pretty_root_name(i)])
            for k,v in vars(i).items():
                if isinstance(v, BaseMapParser):
                    current_item = QTreeWidgetItem([str(k)])
                    for kk,vv in v.dict().items():
                        if (isinstance(vv, BaseParser)):
                            current_child = QTreeWidgetItem([str(kk)])
                            for kkk,vvv in vv.dict().items():
                                current_subchild = QTreeWidgetItem([str(kkk), str(vvv)]) # fuck my stupid steamsad life
                                current_child.addChild(current_subchild)
                        else:
                            current_child = QTreeWidgetItem([str(kk), str(vv)])
                        current_item.addChild(current_child)
                elif isinstance(v, BaseParser):
                    current_item = QTreeWidgetItem([str(k)])
                    for k,v in v.dict().items():
                        current_child = QTreeWidgetItem([str(k), str(v)])
                        current_item.addChild(current_child)
                else:
                    current_item = QTreeWidgetItem([str(k), str(v)])
                item.addChild(current_item)
            items.append(item)

        self.main_table.insertTopLevelItems(0,items)

    def __init__(self, _lst :list):
        super(CDRListViewWindow, self).__init__()

        self.lst = _lst

        self.setAttribute(Qt.WA_DeleteOnClose)
        if (self.lst.__class__.__name__ == "UserDefinedRecord"):
            self.setWindowTitle(f"List view UserDefinedRecord (kv)")
        else:
            self.setWindowTitle(f"List view of {self.lst.__class__.__name__}")
        self.resize(500,500)

        self.main_table = QTreeWidget()
        self.main_table.setColumnCount(2)
        self.populate_tree()
        self.layout = QVBoxLayout() 
        self.layout.addWidget(self.main_table)
        self.setLayout(self.layout) 
        #self.show()
        pass
    
    def wnd_name(self):
        return "CDR List View" 

class CDRListViewListWidgetItem(QTableWidgetItem):

    def __init__(self, txt :str, tbl :dict):
        self.ctx_tbl = tbl
        super(CDRListViewListWidgetItem, self).__init__(txt)

class CDRRealListViewWindow(QWidget):

    def populate_tree(self):
        items = []

        for i in self.lst:
            items.append(str(i))

        self.main_table.insertItems(0,items)

    def __init__(self, _lst :list, _table_name : str):
        super(CDRRealListViewWindow, self).__init__()

        self.lst = _lst
        self.table_name = _table_name
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle(self.table_name)
        self.resize(500,500)

        self.main_table = QListWidget()
        self.populate_tree()
        self.layout = QVBoxLayout() 
        self.layout.addWidget(self.main_table)
        self.setLayout(self.layout) 
        #self.show()
        pass
    
    def wnd_name(self):
        return "List view of {self.table_name}"

class CDRRealListViewListWidgetItem(QTableWidgetItem):

    def __init__(self, txt :str, tbl :list, wndtitle :str):
        self.ctx_tbl = tbl
        self.ctx_wndtitle = wndtitle
        super(CDRRealListViewListWidgetItem, self).__init__(txt)