import Queue
import folderwatcher
import filesyncer

class grabSphere:
    def __init__(self):
        self.programmingFolder = '/home/andrew/programming/'
        self.picturesFolder = 'Another Folder'
        self.backupDirectory = 'BACKUP DIRECTORY'
        self.base = '/home/andrew/' 
        
        self.fileQueue = Queue.Queue()
        self.programmingWatcher = folderwatcher.WatchFolder(self.programmingFolder, self.fileQueue).start()
        self.picturesWatcher = folderwatcher.WatchFolder(self.picturesFolder, self.fileQueue).start()
        self.fileSyncer = filesyncer.FileSyncer(self.fileQueue, self.backupDirectory).start()

if __name__ == '__main__':
    a = grabSphere()
