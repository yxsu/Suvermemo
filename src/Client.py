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
        
        #temporary authToken
        self.authToken = "S=s1:U=41d1e:E=142b37de5b4:C=13b5bccb9b8:P=1cd:A=en-devtoken:H=eafd32b1803db02e99f68520ff00a779"
        
        evernoteHost = "sandbox.evernote.com"
        userStoreUri = "https://" + evernoteHost + "/edam/user"

        userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)

        versionOK = userStore.checkVersion("Evernote EDAMTest (Python)",
                                           UserStoreConstants.EDAM_VERSION_MAJOR,
                                           UserStoreConstants.EDAM_VERSION_MINOR)
        if(not versionOK):
            pass 
        
        noteStoreUrl = userStore.getNoteStoreUrl(self.authToken)

        noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        self.note_store = NoteStore.Client(noteStoreProtocol)

    def ListNotebooksInfo(self):
        '''List all of the notebooks in the user's account'''
        self.notebooks, note_counts = self.DownloadNotebookList()
        info = dict()
        for notebook in self.notebooks:
            info[notebook.name] = [note_counts.notebookCounts[notebook.guid], 0, 0]       
        return info
    
    def ShowNextNote(self, notebook_name):
    
        #find the guid of current notebook
        if(notebook_name != None):
            for notebook in self.notebooks:
                if(notebook.name == notebook_name):
                    self.current_notebook_guid = notebook.guid
                    self.LoadNotebook(notebook.guid)
        
        note = random.choice(self.note_list)
        return note.title, note.content
            
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
        info_path = '../data/notebooks/notebook_info'
        #read notebook list and count list
        if(os.path.exists(list_path) and os.path.exists(info_path)):
            list_file = open(list_path)
            info_file = open(info_path)
            notebooks = pickle.load(list_file)
            note_counts = pickle.load(info_file)
            list_file.close()
            info_file.close()
            return notebooks, note_counts
        else:
            notebooks = self.note_store.listNotebooks(self.authToken)
            note_counts = self.note_store.findNoteCounts(self.authToken, NoteStore.NoteFilter(), False)
            list_file = open(list_path, 'w')
            info_file = open(info_path, 'w')
            pickle.dump(notebooks, list_file)
            pickle.dump(note_counts, info_file)
            list_file.close()
            info_file.close()
            return notebooks, note_counts
    
    