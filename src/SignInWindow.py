
from PySide.QtGui import *
from PySide.QtCore import *
from oauth import Auth
import pickle
import os

class SignInWindow(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Login")
        main_layout = QVBoxLayout()
        self.username = QTextEdit()
        self.password = QTextEdit()
        form_layout = QFormLayout()
        form_layout.addRow('Username: ', self.username)
        form_layout.addRow('Password: ', self.password)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        self.button_sign = QPushButton("Sign in")
        main_layout.addWidget(self.button_sign)
        
        self.setLayout(main_layout)
        
        self.button_sign.clicked.connect(self.SignIn)

    def SignIn(self):
        pass
        