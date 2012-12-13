import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import random
import pickle
import os

class Client:
    
    def __init__(self):
        
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

    def ListNotebooksInfo(self):
        '''List all of the notebooks in the user's account'''
        self.notebooks, note_counts = self.DownloadNotebookList()
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
                    self.LoadNotebook(notebook.guid)
        
        note = random.choice(self.note_list)
        return note.title.decode('utf-8'), note.content.decode('utf-8')
            
    def LoadNotebook(self, notebook_guid):
        '''
            if the given notebook is not stored locally, download the notebook first
            else load the notebook from local storage
        '''
        file_path = '../data/notebooks/' + notebook_guid
        if(os.path.exists(file_path)):
            infile = open(file_path)
            self.note_list = pickle.load(infile)
            infile.close()
        else:
            self.note_list = self.DownloadNotes(notebook_guid)
        
    def DownloadNotes(self, notebook_guid):
        
        note_filter = NoteStore.NoteFilter()
        note_filter.notebookGuid = notebook_guid
        NoteStore.NoteList
        note_list = self.note_store.findNotes(self.authToken, note_filter, 0, 10000)
        #download the content of note
        for note in note_list.notes:
            note.content = self.note_store.getNoteContent(self.authToken, note.guid)
        #save note_list to file
        saved_file = open('../data/notebooks/' + notebook_guid, 'w')
        pickle.dump(note_list.notes, saved_file)
        saved_file.close()
        return note_list.notes
    
    def DownloadNotebookList(self):
        list_path = '../data/notebooks/notebook_list'
        #read notebook list and count list
        if(os.path.exists(list_path)):
            list_file = open(list_path)
            notebooks, note_counts = pickle.load(list_file)
            list_file.close()
            return notebooks, note_counts
        else:
            notebooks = self.note_store.listNotebooks(self.authToken)
            note_counts = self.note_store.findNoteCounts(self.authToken, NoteStore.NoteFilter(), False)
            list_file = open(list_path, 'w')
            pickle.dump([notebooks, note_counts], list_file)
            list_file.close()
            return notebooks, note_counts
    
    