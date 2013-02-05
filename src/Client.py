import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import random
import pickle
import os
import time
from PySide.QtGui import QProgressDialog
from PySide.QtCore import Qt
from datetime import timedelta, date

class Client:
    
    
    def __init__(self):
        self.notebook_base_path = '../data/notebooks/'
        self.notebook_list_path = '../data/notebooks/notebook_list'
    
    def MakeConnectionWithEvernote(self):
        self.authToken = "S=s43:U=47f934:E=142e9b9232d:C=13b9207f72d:P=1cd:A=en-devtoken:H=55aee67673b98b2067e1576270845445"
        evernoteHost = "www.evernote.com"
        userStoreUri = "https://" + evernoteHost + "/edam/user"
        userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)
        noteStoreUrl = userStore.getNoteStoreUrl(self.authToken)
        noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        self.note_store = NoteStore.Client(noteStoreProtocol)
        print("The connection with evernote.com is established")

    def ListNotebooksInfo(self):
        '''List all of the notebooks in the user's account'''
        self.notebooks, note_counts = self.LoadNotebookList()
        info = dict()
        for notebook in self.notebooks:
            info[notebook.name.decode('utf-8')] = [note_counts.notebookCounts[notebook.guid], 0, 0]       
        return info
    
    def ShowNextNote(self, notebook_name):
    
        #find the guid of current notebook
        if(notebook_name != None):
            for notebook in self.notebooks:
                if(notebook.name.decode('utf-8') == notebook_name):
                    self.current_notebook_guid = notebook.guid
                    self.LoadNotebookContent(notebook.guid)
        #remove the future note
        for note in self.note_list[:]:
            if(self.timestamp_list[note.guid][0] > date.today()):
                self.note_list.remove(note)
                
        if(len(self.note_list) > 0):
            note = random.choice(self.note_list)
            self.current_note_guid = note.guid
            return note.title.decode('utf-8'), note.content.decode('utf-8')
        else:
            self.SaveTimeStamp()
            return '', "There is nothing left in today's list" 
            
    def SetNewTimeStamp(self, choice):
        
        current_count = self.timestamp_list[self.current_note_guid][1]
        new_count = {'good': 10, 'pass': current_count + 1, 'fail': current_count - 1, 'bad': -10}
        self.timestamp_list[self.current_note_guid][1] = new_count[choice]
        #set the next time
        self.timestamp_list[self.current_note_guid][0] = date.today() +  timedelta(days = self.Fib(new_count[choice]))
        
    def Fib(self, n):
        if(n < 1):
            return 0
        else:
            a, b =1, 1
            for i in range(n):
                a, b = a + b, a
            return a
                   
    def LoadNotebookContent(self, notebook_guid):
        '''
            if the given notebook is not stored locally, download the notebook first
            else load the notebook from local storage
        '''
        file_path = self.notebook_base_path + notebook_guid
        timestamp_path = self.notebook_base_path + 'time_' + notebook_guid
        if(os.path.exists(file_path) and os.path.exists(timestamp_path)):
            infile = open(file_path, 'r')
            self.note_list = pickle.load(infile)
            infile.close()
            self.SaveTimeStamp()
            infile = open(timestamp_path, 'r')
            self.timestamp_list = pickle.load(infile)
            infile.close()
        else:
            self.MakeConnectionWithEvernote()
            self.DownloadNotes(notebook_guid)
        
        
    def DownloadNotes(self, notebook_guid):
        #set progress dialog
        progress = QProgressDialog("Read data from server...", "Abort downloading", 0, 100)
        progress.setWindowModality(Qt.WindowModal)
        #read note data from server
        note_filter = NoteStore.NoteFilter()
        note_filter.notebookGuid = notebook_guid
        offset = 0
        note_list = self.note_store.findNotes(self.authToken, note_filter, 0, 10000)
        full_note_list = note_list.notes
        while(len(full_note_list) < note_list.totalNotes):
            offset = offset + len(note_list.notes)
            note_list = self.note_store.findNotes(self.authToken, note_filter, offset, 10000)
            full_note_list.extend(note_list.notes)
        #set content of progress dialog
        progress.setMaximum(len(full_note_list))
        progress.setLabelText("Downloading content of notebook...")
        #download the content of note
        if(not hasattr(self, 'note_list')):
            self.note_list = []
            self.timestamp_list = dict()
            guid_list = []
        else:
            guid_list = [note.guid for note in self.note_list]
            
        count = 0
        for note in full_note_list:
            #load content
            if(note.guid not in guid_list):
                #add new note
                note.content = self.note_store.getNoteContent(self.authToken, note.guid)
                self.note_list.append(note)
                self.timestamp_list[note.guid] = [date.today(), 0]
            else:
                #update existed note
                note_index = guid_list.index(note.guid)
                if(self.note_list[note_index].updated < note.updated):
                    self.note_list[note_index].content = self.note_store.getNoteContent(self.authToken, note.guid)
            #set counter
            progress.setValue(count)
            count = count + 1
            if(progress.wasCanceled()):
                raise RuntimeError("Downloading was canceled")
        #save note_list to file
        saved_file = open(self.notebook_base_path + notebook_guid, 'w')
        pickle.dump(self.note_list, saved_file)
        saved_file.close()
        #save timestamp file
        timestamp_file = open(self.notebook_base_path + 'time_' + notebook_guid, 'w')
        pickle.dump(self.timestamp_list, timestamp_file)
        timestamp_file.close()
    
    def LoadNotebookList(self):
        #read notebook list and count list
        list_file = open(self.notebook_list_path)
        notebooks, note_counts = pickle.load(list_file)
        list_file.close()
        return notebooks, note_counts
    
    def UpdateNotebookList(self):
        notebooks = self.note_store.listNotebooks(self.authToken)
        note_counts = self.note_store.findNoteCounts(self.authToken, NoteStore.NoteFilter(), False)
        list_file = open(self.notebook_list_path, 'w')
        pickle.dump([notebooks, note_counts], list_file)
        list_file.close()
        
    def SaveTimeStamp(self):
        if(hasattr(self, 'timestamp_list')):
            timestamp_file = open(self.notebook_base_path + 'time_' + self.current_notebook_guid, 'w')
            pickle.dump(self.timestamp_list, timestamp_file)
            timestamp_file.close()
            
    def UpdateLocalNotebooks(self):
        print("update local notebooks...")
        notebook_list, note_count = self.LoadNotebookList()
        for notebook in notebook_list:
            file_path = self.notebook_base_path + notebook.guid
            timestamp_path = self.notebook_base_path + 'time_' + notebook.guid
            if(os.path.exists(file_path) and os.path.exists(timestamp_path)):
                infile = open(file_path, 'r')
                self.note_list = pickle.load(infile)
                infile.close()
                self.SaveTimeStamp()
                infile = open(timestamp_path, 'r')
                self.timestamp_list = pickle.load(infile)
                infile.close()
                self.DownloadNotes(notebook.guid)
        print("finished")