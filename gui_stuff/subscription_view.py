from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (
        QMdiArea, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView)
from cdr import BaseMapParser
from gui_stuff.utl_widgets import CDRListViewListWidgetItem, CDRListViewWindow, CDRRealListViewListWidgetItem, CDRRealListViewWindow, copy_to_clipboard


class SubscriptionRecordWindow(QWidget):

    def on_table_click(self, item):
        if isinstance(item, CDRListViewListWidgetItem):
            wnd = CDRListViewWindow(item.ctx_tbl)
            self.mdiarea.addSubWindow(wnd)
            wnd.show()
            return
        if isinstance(item, CDRRealListViewListWidgetItem):

            tbl = []
            for i in item.ctx_tbl:
                tbl.append(f"{i} ({self.cdr.ApplicationRecord[i].Name if i in self.cdr.ApplicationRecord.dict() else "n/a :p" })")
            wnd = CDRRealListViewWindow(tbl, item.ctx_wndtitle)
            self.mdiarea.addSubWindow(wnd)
            wnd.show()
            return
        if isinstance(item, QTableWidgetItem):
            copy_to_clipboard(item.text())

    def populate_table(self):

        fields = [
            "SubscriptionId",
            "Name",
            "BillingType",
            "CostInCents",
            "PeriodInMinutes",
            "AppIdsRecord",
            "RunAppId",
            "OnSubscribeRunLaunchOptionIndex",
            "OptionalRateLimitRecord",
            "DiscountsRecord",
            "IsPreorder",
            "RequiresShippingAddress",
            "DomesticCostInCents",
            "InternationalCostInCents",
            "RequiredKeyType",
            "IsCyberCafe",
            "GameCode",
            "GameCodeDescription",
            "IsDisabled",
            "RequiresCD",
            "TerritoryCode", 
            "IsSteam3Subscription",
            "ExtendedInfoRecord",
        ]

        nametoid = {
            "SubscriptionId" : 0,
            "Name" : 1,
            "BillingType" : 2,
            "CostInCents" : 3,
            "PeriodInMinutes" : 4,
            "AppIdsRecord" : 5,
            "RunAppId" : 6,
            "OnSubscribeRunLaunchOptionIndex":7,
            "OptionalRateLimitRecord":8,
            "DiscountsRecord":9,
            "IsPreorder":10,
            "RequiresShippingAddress":11,
            "DomesticCostInCents":12,
            "InternationalCostInCents":13,
            "RequiredKeyType":14,
            "IsCyberCafe":15,
            "GameCode":16,
            "GameCodeDescription":17,
            "IsDisabled":18,
            "RequiresCD":19,
            "TerritoryCode":20, 
            "IsSteam3Subscription":21,
            "ExtendedInfoRecord":22,
        }

        self.main_table.setRowCount(len(self.cdr.SubscriptionRecord.dict()))
        self.main_table.setColumnCount(len(fields)-1)

        self.main_table.setHorizontalHeaderLabels(fields[1:])
        self.sorted_dict = {str(k): v for k, v in sorted(self.cdr.SubscriptionRecord.dict().items(), key=lambda item: item[1].SubscriptionId)}
        self.main_table.setVerticalHeaderLabels(self.sorted_dict.keys())
        i = 0
        for v in self.sorted_dict.values():
            for kk,vv in vars(v).items():
                if kk == "SubscriptionId":
                    continue
                
                if isinstance(vv, BaseMapParser):  
                    if len(vv.dict()) != 0:
                        self.main_table.setItem(i,nametoid[kk]-1, CDRListViewListWidgetItem("Click to view", vv))
                    else:
                        self.main_table.setItem(i,nametoid[kk]-1, QTableWidgetItem("n/a"))
                    continue
                elif kk == "AppIdsRecord":
                    self.main_table.setItem(i,nametoid[kk]-1, CDRRealListViewListWidgetItem("Click to view", vv, f"Apps in subscription {v.Name}"))
                    continue


                self.main_table.setItem(i,nametoid[kk]-1, QTableWidgetItem(str(vv)))
            i += 1

    def __init__(self, cdr_dict : dict, mdiarea : QMdiArea):
        self.cdr = cdr_dict

        self.mdiarea = mdiarea
        super(SubscriptionRecordWindow, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Subscription Record")
        self.resize(500,500)
        self.main_table = QTableWidget()
        self.main_table.itemDoubleClicked.connect(self.on_table_click)
        self.main_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.populate_table()
        self.layout = QVBoxLayout() 
        self.layout.addWidget(self.main_table)
        self.setLayout(self.layout) 
    
    def wnd_name(self):
        return "Subscription Record"
