

from PySide.QtGui import *
from PySide.QtCore import *
import sys

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Suvermemo -- Powered by Su Yuxin")
        self.SetupLayout()
        self.SetupMenus()

    def SetupLayout(self):
        
        self.note_title = QLabel("Title:")
        
        self.question = QTextEdit()
        self.question.setReadOnly(True)

        self.answer = QTextEdit()
        self.answer.setMaximumHeight(200)
        self.answer.setReadOnly(True)
        
        self.good_button = QPushButton("Good")
        self.pass_button = QPushButton("Pass")
        self.fail_button = QPushButton("Fail")
        self.bad_button = QPushButton("Bad")

        button_box = QHBoxLayout()
        button_box.addWidget(self.good_button)
        button_box.addWidget(self.pass_button)
        button_box.addWidget(self.fail_button)
        button_box.addWidget(self.bad_button)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.note_title)
        vbox.addWidget(self.question)
        vbox.addWidget(self.answer)
        vbox.addLayout(button_box)

        self.progress_bar = QProgressBar()
        self.progress_bar.setOrientation(Qt.Vertical)
        self.progress_bar.setTextDirection(QProgressBar.TopToBottom)

        main_hbox = QHBoxLayout()
        main_hbox.addLayout(vbox)
        main_hbox.addWidget(self.progress_bar)

        frame = QFrame()
        frame.setLayout(main_hbox)
        self.setCentralWidget(frame)

    def SetupMenus(self):
        self.account_menu = self.menuBar().addMenu("Account")
        
        self.sign_in_action = QAction("Sign in...", self)
        self.account_menu.addAction(self.sign_in_action)

        self.choose_notebook_action = QAction("Choose Notebook", self)
        self.account_menu.addAction(self.choose_notebook_action)

        self.sync_action = QAction("Sync", self)
        self.account_menu.addAction(self.sync_action)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
