
from PySide.QtGui import *
from PySide.QtCore import Qt

class NotebookList(QDialog):
    def __init__(self, notebook_info, parent=None):
        super(NotebookList, self).__init__(parent)
        self.setWindowTitle("Choose a Notebook to review")
        self.setMinimumSize(600, 300)
        self.SetItemModel(notebook_info)
        self.SetItemView()
        
    def SetItemModel(self, notebook_info):
        '''add notebook information to item model'''
        self.model = QStandardItemModel(0, 4, self)
        self.model.setHeaderData(0, Qt.Horizontal, "Name")
        self.model.setHeaderData(1, Qt.Horizontal, "Count")
        self.model.setHeaderData(2, Qt.Horizontal, "To Review")
        self.model.setHeaderData(3, Qt.Horizontal, "Marked as Good")
        for name, data in notebook_info.items():
            self.model.insertRow(0)
            self.model.setData(self.model.index(0, 0), name)
            for i in range(3):
                self.model.setData(self.model.index(0, i + 1), data[i])
        
    def SetItemView(self):
        self.tree_view = QTreeView()
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setModel(self.model)
        self.tree_view.doubleClicked.connect(self.accept)
        vbox = QVBoxLayout()
        vbox.addWidget(self.tree_view)
        self.setLayout(vbox)
        
    def accept(self):
        self.selected_notebook = (self.tree_view.selectedIndexes())[0].data(0)
        super(NotebookList, self).accept()