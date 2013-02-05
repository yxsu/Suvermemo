#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
import re
import sys
from Client import Client
from NotebookList import NotebookList

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Suvermemo -- Powered by Su Yuxin")
        self.setMinimumSize(700, 500)
        self.font_size = 24
        self.SetupLayout()
        self.SetupMenus()
        self.SetupConnection()
        self.client = Client()
        
    def event(self, evt):
        event_type = evt.type()
        
        if(event_type == QEvent.Close):
            self.client.SaveTimeStamp()
            evt.ignore()
            QCoreApplication.quit()
            return False
        else:
            return super(MainWindow, self).event(evt)
        

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
        self.show_answer_button = QPushButton("Show Answer")
        #set initial visible
        self.SetVisibleOfButtonBox(False)
        #set layout of buttons
        button_box = QHBoxLayout()
        button_box.addWidget(self.show_answer_button)
        button_box.addWidget(self.good_button)
        button_box.addWidget(self.pass_button)
        button_box.addWidget(self.fail_button)
        button_box.addWidget(self.bad_button)
        #set main layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.note_title)
        vbox.addWidget(self.question)
        vbox.addWidget(self.answer)
        vbox.addLayout(button_box)
        #set progress bar
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

        self.choose_notebook_action = QAction("Choose Notebook", self)
        self.account_menu.addAction(self.choose_notebook_action)

        self.sync_action = QAction("Sync with suyuxin's account", self)
        self.account_menu.addAction(self.sync_action)
        
    def SetupConnection(self):
        self.sync_action.triggered.connect(self.SyncWithAccount)
        self.choose_notebook_action.triggered.connect(self.ChooseNotebook)
        self.show_answer_button.clicked.connect(self.ShowAnswer)
        #set the connection of evaluation
        self.good_button.clicked.connect(lambda : self.Evaluation("good"))
        self.pass_button.clicked.connect(lambda : self.Evaluation("pass"))
        self.fail_button.clicked.connect(lambda : self.Evaluation("fail"))
        self.bad_button.clicked.connect(lambda : self.Evaluation("bad"))
        
    def SetVisibleOfButtonBox(self, to_evalute):
        self.show_answer_button.setVisible(not to_evalute)
        self.good_button.setVisible(to_evalute)
        self.pass_button.setVisible(to_evalute)
        self.fail_button.setVisible(to_evalute)
        self.bad_button.setVisible(to_evalute)
            
    def ShowNextNote(self, notebook_name = None):
        if(self.client):
            try:
                data = self.client.ShowNextNote(notebook_name)#data = [title content]
                self.note_title.setText('Title : ' + data[0])
                question, self.answer_list = self.ExtractTheAnswer(data[1])
                self.current_answer_index = 0
                self.question.setText(question)
                self.answer.setText("")    
            except RuntimeError:
                pass
            
    def ShowAnswer(self):
        if(self.current_answer_index < len(self.answer_list)):
            answer = '<?xml version="1.0" encoding="UTF-8"?>' + \
                     '<body style="font-size: '+str(self.font_size)+'pt; ">'
            for index in range(self.current_answer_index + 1):
                answer = answer + '<p>' + self.answer_list[index] + '</p>'
            answer = answer + '</body>'
            self.answer.setText(answer)
            self.current_answer_index = self.current_answer_index + 1
        if(self.current_answer_index >= len(self.answer_list)):
            self.SetVisibleOfButtonBox(True)
        
    def SyncWithAccount(self):
        self.client.MakeConnectionWithEvernote()
        self.client.UpdateNotebookList()
        self.client.UpdateLocalNotebooks()
        print("Evernote account is estabilished")
        
    def ChooseNotebook(self):
        try:
            notebook_info = self.client.ListNotebooksInfo()
            notebook = NotebookList(notebook_info, self)
            notebook.exec_()
            self.setWindowTitle('Suvermemo - ' + notebook.selected_notebook)
            self.ShowNextNote(notebook.selected_notebook)
            self.notes_number = len(self.client.note_list)
            self.progress_bar.setMaximum(self.notes_number)
        except IOError:
            QMessageBox.information(self, "Suvermemo", "The notebook list doesn't exist in client.\
                                                    You should sync with Evernote account first")
        except:
            raise
        
    def Evaluation(self, choice):
        #save result
        self.client.SetNewTimeStamp(choice)
        self.SetVisibleOfButtonBox(False)
        self.progress_bar.setValue(self.notes_number - len(self.client.note_list))
        self.ShowNextNote()
        
    def ExtractTheAnswer(self, question):
        #set font size
        position = question.index("<en-note style=")
        question = question[:position + 16] + "font-size: "+str(self.font_size)+ "pt; " +question[position+17:]
        #find answer
        span_style = re.compile('<span style="color.*?</span>')
        font_style = re.compile('<font color.*?</font>')
        start_pos = 0
        answer_list = []
        while(True):
            result = font_style.search(question, start_pos)
            if(result == None):
                break
            sub_string = result.group()
            answer_list.append(sub_string)
            question = question.replace(sub_string[22: -7], ' [......] ')
            start_pos = (result.start() + result.end()) / 2
        start_pos = 0
        while(True):
            result = span_style.search(question, start_pos)
            if(result == None):
                break
            sub_string = result.group(0)
            answer_list.append(sub_string)
            question = question.replace(sub_string[30: -7], ' [......] ')
            start_pos = result.end(0)
        return question, answer_list
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
