import Queue
import folderwatcher
import filesyncer
import os
import time
import sys
import pickle

class grabSphere:
    def __init__(self, backupRoot, homeRoot, folderList=None):
        # backupRoot and homeRoot are the base directories
        # where the rest of the folders are assembled from.
        # There's probably a better way to do this.
        self.backupRoot = backupRoot
        self.homeRoot = homeRoot
        
        # If you pass in a folder list, it will watch all those.
        if folderList:
            self.watchList = folderList
        else:
            self.programmingFolder = 'testdir/'
            self.picturesFolder = 'Pictures/'
            self.watchList = [self.programmingFolder]
        
        
        self.fileQueue = Queue.Queue()
        
        for folder in self.watchList:
            if folder[-1] is not '/':
                folder += '/'
            homeFolder = self.homeRoot + folder
            backupFolder = self.backupRoot + folder
            
            if not os.path.isdir(backupFolder):
                print '%s not present, attempting to make it.' %backupFolder
                os.mkdir(backupFolder)
            
            hi = folderwatcher.WatchFolder(homeFolder, backupFolder, self.fileQueue)
            hi.start()
            time.sleep(.25)
            
        fileSyncer = filesyncer.FileSyncer(self.fileQueue).start()
        
if __name__ == '__main__':
    print 'Initializing controller for file syncing.'
    
    homeRoot = '/home/andrew/'
    folders = ['Documents/']
    backupFolder = '/mnt/ExtTV/DesktopBackup/'

    if os.path.isdir(backupFolder):
        print 'Backup folder is:', backupFolder
    else:
        print 'Is the Backup path you entered correct?'

    a = grabSphere(backupFolder, homeRoot, folders)
