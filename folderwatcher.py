import threading
import time
import os
import Queue

class WatchFolder(threading.Thread):
    def __init__(self, homePath, backupPath, backupFileQueue):
        threading.Thread.__init__(self)
        self.fileQueue = backupFileQueue
        self.homePath = homePath
        self.backupPath = backupPath
        self.sleepTime = 5
        self.newCheck = 4*self.sleepTime
        os.chdir(self.homePath)
        self.files = self.getFileList(self.homePath, self.backupPath)
        self.backupFiles = self.getFileList(self.backupPath, self.homePath)
        print 'FolderWatcher watching %s files in %s' %(len(self.files), self.homePath)
        print 'FolderWatcher watching %s files in %s' %(len(self.backupFiles), self.backupPath)
        
    def getFiles(self):
        return self.files
        
    def run(self):
        self.watchFolder()
        
    def watchFolder(self):
        timer = 0
        
        while True:
            self.checkForModifiedFiles(self.files)
            time.sleep(self.sleepTime)
            self.checkForModifiedFiles(self.backupFiles)
            
            timer += self.sleepTime
            if timer == self.newCheck:
                timer = 0
                self.files = self.checkForNewFiles(self.files, self.homePath)
                self.backupFiles = self.checkForNewFiles(self.backupFiles, self.backupPath)
                if len(self.backupFiles) is not len(self.files):
                    for f in self.backupFiles:
                        if not self.files.has_key(f):
                            self.fileQueue.put(self.backupFiles[f])
                    for f in self.files:
                        if not self.backupFiles.has_key(f):
                            self.fileQueue.put(self.files[f])
                else:
                    print 'Files synchronized.'

    def checkForNewFiles(self, files, path):
        if path == self.backupPath:
            newFiles = self.getFileList(path, self.homePath)
        else:
            newFiles = self.getFileList(path, self.backupPath)
            
        for newFile in newFiles:
            if not files.has_key(newFile):
                self.fileQueue.put(newFiles[newFile])
            else:
                print 'No new file changes.'
        files = newFiles
        print 'FolderWatcher watching %s files in %s' %(len(files), path)
        return files
        
    def checkForModifiedFiles(self, files):
        for f in files:
            fullPath = files[f]['fullpath']
            modTime = os.path.getmtime(fullPath)
            if (modTime > files[f]["modtime"]):
                #if files[f]['md5'] is not md5er.filemd5(fullPath):
                files[f]["modtime"] = os.path.getmtime(fullPath)
                self.fileQueue.put(files[f])
    
    def getFileList(self, path, backupPath):
        files = {}
        for f in os.listdir(path):
            filePath = path+f
            if os.path.isfile(filePath):
                if f[-1] is not '~':
                    modtime = os.path.getmtime(filePath)
                    files[f] = {'filename': f, 'modtime':modtime, 'fullpath':filePath, 'backuppath':backupPath}
        return files
        
if __name__ == '__main__':
    q = Queue.Queue()
    homePath = '/home/andrew/Pictures/'
    backupPath = '/mnt/ExtTV/DesktopBackup/Pictures/'
    pictures = WatchFolder(homePath, backupPath, q)
    pictures.start()
    while True:
        if q.not_empty:
            print q.get()
            
