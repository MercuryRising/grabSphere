import Queue
import folderwatcher
import filesyncer
import os
import time
import sys

class grabSphere:
    def __init__(self, folderList = None):
    
        self.backupRoot = '/mnt/ExtTV/DesktopBackup/'
        self.homeRoot = '/home/andrew/'
        
        if folderList:
            self.watchList = folderList
        else:
            self.programmingFolder = 'testdir/'
            self.picturesFolder = 'Pictures/'
            self.watchList = [self.programmingFolder]
        
        self.fileQueue = Queue.Queue()
        
        for folder in self.watchList:
            homeFolder = self.homeRoot + folder
            backupFolder = self.backupRoot + folder
            print 'Backup Folder ', backupFolder
            if not os.path.isdir(backupFolder):
                os.mkdir(backupFolder)
            hi = folderwatcher.WatchFolder(homeFolder, backupFolder, self.fileQueue)
            hi.start()
            back = folderwatcher.WatchFolder(backupFolder, homeFolder, self.fileQueue)
            back.start()
            time.sleep(.25)
            backupFiles = back.getFiles()
            sourceFiles = hi.getFiles()
            for f in sourceFiles:
                if not backupFiles.has_key(f):
                    self.fileQueue.put(sourceFiles[f])
            for f in backupFiles:
                if not sourceFiles.has_key(f):
                    self.fileQueue.put(backupFiles[f])
        fileSyncer = filesyncer.FileSyncer(self.fileQueue).start()
        
if __name__ == '__main__':
    a = grabSphere()
