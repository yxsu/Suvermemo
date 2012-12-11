import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import random

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
        self.notebooks = self.note_store.listNotebooks(self.authToken)
        note_counts = self.note_store.findNoteCounts(self.authToken, NoteStore.NoteFilter(), False)
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
        
            note_filter = NoteStore.NoteFilter()
            note_filter.notebookGuid = self.current_notebook_guid
            self.note_list = self.note_store.findNotes(self.authToken, note_filter, 0, 1000)
    
        rand_index = random.randrange(self.note_list.startIndex, self.note_list.totalNotes)
        note = self.note_list.notes[rand_index]
        return note.title, self.note_store.getNoteContent(self.authToken, note.guid)
            
    
    
    
    
    
    